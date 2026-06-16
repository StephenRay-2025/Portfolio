#!/usr/bin/env python3
"""
Pricing module for AM4 Aircraft Dashboard.

Provides functions to fetch current fuel and CO2 prices from the am4-prices API,
and to compute ticket prices, revenue, fuel cost, and CO2 cost based on
aircraft, route, and seat configuration.
"""

from __future__ import annotations

import datetime
import time
from typing import Dict, Tuple, Optional

from am4_prices.api import AM4APIClient
from am4_prices.models import PricesData, DayPrices, PricePoint

# Global cache for price data to avoid frequent HTTP requests
_price_cache: Tuple[float, PricesData] = (0.0, None)  # (timestamp, data)
_CACHE_TTL = 300  # 5 minutes


def _get_price_data() -> PricesData:
    """
    Fetch or return cached price data.
    Refreshes if cache is older than _CACHE_TTL seconds.
    """
    global _price_cache
    now = time.time()
    if now - _price_cache[0] > _CACHE_TTL or _price_cache[1] is None:
        client = AM4APIClient()
        data = client.fetch_prices()
        _price_cache = (now, data)
    return _price_cache[1]


def get_current_fuel_price() -> int:
    """
    Get the current fuel price (in-game currency) based on current UTC time.
    Returns the fuel price for the nearest 30-minute interval.
    """
    data = _get_price_data()
    now = datetime.datetime.utcnow()
    day = now.day
    day_prices: DayPrices = data.get_day(day)
    price_point: PricePoint = day_prices.get_current_price(now)
    return price_point.fuel


def get_current_co2_price() -> int:
    """
    Get the current CO2 price (in-game currency) based on current UTC time.
    Returns the CO2 price for the nearest 30-minute interval.
    """
    data = _get_price_data()
    now = datetime.datetime.utcnow()
    day = now.day
    day_prices: DayPrices = data.get_day(day)
    price_point: PricePoint = day_prices.get_current_price(now)
    return price_point.co2


def calculate_ticket_price(
    distance_km: float,
    seat_class: str,
    mode: str = "easy",
    optimal: bool = True,
) -> float:
    """
    Calculate ticket price for a given seat class and distance.

    Parameters
    ----------
    distance_km : float
        Great-circle distance in kilometres.
    seat_class : str
        One of 'Y' (economy), 'J' (business), 'F' (first).
    mode : str, optional
        Either 'easy' or 'realism'. Defaults to 'easy'.
    optimal : bool, optional
        If True, apply the optimal price multiplier (1.1/1.08/1.06 for easy,
        1.22/1.195/1.175 for realism). If False, use the autoprice.
        Defaults to True.

    Returns
    -------
    float
        Ticket price in-game currency.
    """
    # Base formulas from the webpage (easy mode)
    if mode.lower() == "easy":
        if seat_class == "Y":
            base = 0.4 * distance_km + 170
        elif seat_class == "J":
            base = 0.8 * distance_km + 560
        elif seat_class == "F":
            base = 1.2 * distance_km + 1200
        else:
            raise ValueError(f"Invalid seat class: {seat_class}")
        if optimal:
            multipliers = {"Y": 1.1, "J": 1.08, "F": 1.06}
            base *= multipliers[seat_class]
    elif mode.lower() == "realism":
        if seat_class == "Y":
            base = 0.3 * distance_km + 150
        elif seat_class == "J":
            base = 0.6 * distance_km + 500
        elif seat_class == "F":
            base = 0.9 * distance_km + 1000
        else:
            raise ValueError(f"Invalid seat class: {seat_class}")
        if optimal:
            multipliers = {"Y": 1.22, "J": 1.195, "F": 1.175}
            base *= multipliers[seat_class]
    else:
        raise ValueError(f"Invalid mode: {mode}")
    return base


def calculate_revenue(
    distance_km: float,
    seat_config: Dict[str, int],
    load_factor: float = 0.75,
    mode: str = "easy",
    optimal: bool = True,
) -> float:
    """
    Calculate expected revenue for a flight.

    Parameters
    ----------
    distance_km : float
        Great-circle distance in kilometres.
    seat_config : dict
        Mapping of seat class to number of seats.
        Expected keys: 'Y', 'J', 'F' (economy, business, first).
    load_factor : float, optional
        Proportion of seats expected to be filled (0-1). Defaults to 0.75.
    mode : str, optional
        'easy' or 'realism'. Defaults to 'easy'.
    optimal : bool, optional
        Whether to apply optimal price multipliers. Defaults to True.

    Returns
    -------
    float
        Revenue in-game currency.
    """
    revenue = 0.0
    for cls, seats in seat_config.items():
        if cls not in ("Y", "J", "F"):
            continue
        price = calculate_ticket_price(distance_km, cls, mode=mode, optimal=optimal)
        revenue += price * seats
    return revenue * load_factor


def calculate_fuel_cost(
    distance_km: float,
    fuel_per_hour: float,
    speed_kmh: float,
    ci: int = 0,
    fuel_price: Optional[int] = None,
) -> float:
    """
    Calculate fuel cost for a flight.

    Uses the simplified model: fuel_consumed = fuel_per_hour * flight_time.
    For more accuracy, one could use the formula from the webpage:
        fuel = (1 - tf) * ceil(d,2) * cf * (CI/500 + 0.6)
    but requires fuel training amount (tf). We'll use the simpler model.

    Parameters
    ----------
    distance_km : float
        Great-circle distance in kilometres.
    fuel_per_hour : float
        Aircraft fuel consumption in kg/h (from dataset).
    speed_kmh : float
        Aircraft cruise speed in km/h.
    ci : int, optional
        Cost index (0-200). Defaults to 0.
    fuel_price : int, optional
        Current fuel price. If None, fetches from API.

    Returns
    -------
    float
        Fuel cost in-game currency.
    """
    if fuel_price is None:
        fuel_price = get_current_fuel_price()
    flight_time_hr = distance_km / speed_kmh if speed_kmh > 0 else float("inf")
    # Simplified fuel consumption: fuel_per_hour * flight_time
    fuel_consumed = fuel_per_hour * flight_time_hr
    return fuel_consumed * fuel_price


def calculate_co2_cost(
    distance_km: float,
    co2_per_hour: float,
    speed_kmh: float,
    ci: int = 0,
    co2_price: Optional[int] = None,
) -> float:
    """
    Calculate CO2 cost for a flight.

    Uses simplified model: co2_emitted = co2_per_hour * flight_time.

    Parameters
    ----------
    distance_km : float
        Great-circle distance in kilometres.
    co2_per_hour : float
        Aircraft CO2 emission in kg/h (from dataset).
    speed_kmh : float
        Aircraft cruise speed in km/h.
    ci : int, optional
        Cost index (0-200). Defaults to 0.
    co2_price : int, optional
        Current CO2 price. If None, fetches from API.

    Returns
    -------
    float
        CO2 cost in-game currency.
    """
    if co2_price is None:
        co2_price = get_current_co2_price()
    flight_time_hr = distance_km / speed_kmh if speed_kmh > 0 else float("inf")
    co2_emitted = co2_per_hour * flight_time_hr
    return co2_emitted * co2_price