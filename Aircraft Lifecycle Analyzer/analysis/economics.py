#!/usr/bin/env python3
"""
Economics model layer for the AM4 Aircraft Dashboard.

This module converts raw simulation features (aircraft, route, airport data)
into economic metrics: revenue, cost, profit, ROI, and upgrade analysis.
All calculations are based on explicit, configurable assumptions.
Now integrates with am4-prices for live fuel and CO2 prices.
"""

from __future__ import annotations

import math
from typing import Dict, Any, Tuple, Optional

# Local imports – reuse existing services and mapping layer
from datasets import dataset_service
import mapping
import pricing


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great‑circle distance in kilometres using the haversine formula.
    """
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _get_assumptions(custom: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    Return a dictionary of economic assumptions, overriding defaults with any
    user‑provided values.
    """
    defaults: Dict[str, float] = {
        "base_price_per_seat_km": 0.10,   # currency units per seat‑km (kept for compatibility)
        "load_factor": 0.75,              # proportion of seats filled
        "fuel_cost_per_kg": 0.80,         # kept for compatibility; now using live prices
        "co2_cost_per_kg": 0.02,          # kept for compatibility
        "maintenance_cost_per_flight": 50.0,  # fixed cost per flight
        "utilization_flights_per_day": 2.0,
        "days_per_year": 365.0,
    }
    if custom:
        defaults.update(custom)
    return defaults


def compute_flight_economics(
    aircraft_shortname: str,
    origin_iata: str,
    dest_iata: str,
    seat_config: Dict[str, int],
    assumptions: Optional[Dict[str, Any]] = None,
    ticket_price_mode: str = "easy",
    ticket_price_optimal: bool = True,
) -> Dict[str, Any]:
    """
    Compute revenue, cost, profit, and related metrics for a single flight.

    Parameters
    ----------
    aircraft_shortname: str
        Aircraft identifier as entered in the UI (name or shortname).
    origin_iata: str
        Origin IATA code (e.g., "PEK").
    dest_iata: str
        Destination IATA code (e.g., "SIN").
    seat_config: dict
        Mapping of seat class to number of seats.
        Expected keys: 'Y', 'J', 'F' (economy, business, first).
    assumptions: dict, optional
        Override default economic assumptions (see _get_assumptions).
    ticket_price_mode: str, optional
        'easy' or 'realism' for ticket price formula. Defaults to 'easy'.
    ticket_price_optimal: bool, optional
        Whether to apply optimal price multipliers. Defaults to True.

    Returns
    -------
    dict
        Contains intermediate and final economic values:
        - distance_km, flight_time_hr
        - revenue, fuel_cost, co2_cost, operating_cost, total_cost
        - profit (per flight)
        - profit_per_day, profit_per_year (based on assumptions)
        - plus the input aircraft/airport names for convenience.
    """
    # ------------------------------------------------------------------
    # 1. Resolve UI inputs to internal IDs (for validation & lookup)
    # ------------------------------------------------------------------
    _ = mapping.resolve_aircraft(aircraft_shortname)  # will raise ValueError if not found
    origin_id = mapping.resolve_airport(origin_iata)
    dest_id = mapping.resolve_airport(dest_iata)

    # ------------------------------------------------------------------
    # 2. Fetch full rows for aircraft and airports
    # ------------------------------------------------------------------
    ac_row = dataset_service.get_aircraft_by_name(aircraft_shortname)
    if ac_row is None:
        raise ValueError(f"Aircraft '{aircraft_shortname}' not found")
    ori_row = dataset_service.get_airport_by_code(origin_iata.upper())
    dest_row = dataset_service.get_airport_by_code(dest_iata.upper())
    if ori_row is None or dest_row is None:
        raise ValueError(f"Airport not found for IATA {origin_iata} or {dest_iata}")

    # ------------------------------------------------------------------
    # 3. Extract needed attributes
    # ------------------------------------------------------------------
    capacity = float(ac_row.get("capacity", 0.0))                # seats
    fuel_per_hour = float(ac_row.get("fuel", 0.0))               # kg/h
    co2_per_hour = float(ac_row.get("co2", 0.0))                 # kg/h
    speed_kmh = float(ac_row.get("speed", 0.0))                  # km/h
    # Note: `cost` (purchase price) is used later for ROI calculations,
    #        not for per‑flight operating cost here.

    lat1, lon1 = float(ori_row["lat"]), float(ori_row["lng"])
    lat2, lon2 = float(dest_row["lat"]), float(dest_row["lng"])

    # ------------------------------------------------------------------
    # 4. Compute great‑circle distance and flight time
    # ------------------------------------------------------------------
    distance_km = haversine(lat1, lon1, lat2, lon2)
    if speed_kmh <= 0:
        flight_time_hr = float("inf")
    else:
        flight_time_hr = distance_km / speed_kmh

    # ------------------------------------------------------------------
    # 5. Apply assumptions
    # ------------------------------------------------------------------
    ass = _get_assumptions(assumptions)
    LF = ass["load_factor"]                    # load factor
    m = ass["maintenance_cost_per_flight"]     # fixed operating cost per flight
    flights_per_day = ass["utilization_flights_per_day"]
    days_per_year = ass["days_per_year"]

    # ------------------------------------------------------------------
    # 6. Revenue using ticket pricing from pricing.py
    # ------------------------------------------------------------------
    revenue = pricing.calculate_revenue(
        distance_km=distance_km,
        seat_config=seat_config,
        load_factor=LF,
        mode=ticket_price_mode,
        optimal=ticket_price_optimal,
    )

    # ------------------------------------------------------------------
    # 7. Fuel and CO2 costs using live prices from pricing.py
    # ------------------------------------------------------------------
    fuel_price = pricing.get_current_fuel_price()
    co2_price = pricing.get_current_co2_price()
    fuel_cost = pricing.calculate_fuel_cost(
        distance_km=distance_km,
        fuel_per_hour=fuel_per_hour,
        speed_kmh=speed_kmh,
        fuel_price=fuel_price,
    )
    co2_cost = pricing.calculate_co2_cost(
        distance_km=distance_km,
        co2_per_hour=co2_per_hour,
        speed_kmh=speed_kmh,
        co2_price=co2_price,
    )
    operating_cost = m
    total_cost = fuel_cost + co2_cost + operating_cost

    # ------------------------------------------------------------------
    # 8. Profit
    # ------------------------------------------------------------------
    profit = revenue - total_cost

    # ------------------------------------------------------------------
    # 9. Scale‑up metrics (per day / per year) using assumptions
    # ------------------------------------------------------------------
    profit_per_day = profit * flights_per_day
    profit_per_year = profit_per_day * days_per_year

    # ------------------------------------------------------------------
    # 10. Return results
    # ------------------------------------------------------------------
    return {
        "aircraft": ac_row.get("name", aircraft_shortname),
        "aircraft_shortname": ac_row.get("shortname", aircraft_shortname),
        "origin": ori_row.get("iata", origin_iata),
        "destination": dest_row.get("iata", dest_iata),
        "distance_km": distance_km,
        "flight_time_hr": flight_time_hr,
        "revenue": revenue,
        "fuel_cost": fuel_cost,
        "co2_cost": co2_cost,
        "operating_cost": operating_cost,
        "total_cost": total_cost,
        "profit": profit,
        "profit_per_day": profit_per_day,
        "profit_per_year": profit_per_year,
        # Optional: include assumption values for transparency
        "assumptions_used": ass,
        # Also include live prices used
        "fuel_price_used": fuel_price,
        "co2_price_used": co2_price,
    }


def check_route_availability(
    aircraft: str,
    origin_iata: str,
    dest_iata: str,
) -> Dict[str, Any]:
    """
    Check if a given aircraft‑origin‑destination combination exists in route.parquet.

    Parameters
    ----------
    aircraft : str
        Aircraft identifier as entered in UI (name or shortname).
    origin_iata : str
        Origin IATA code.
    dest_iata : str
        Destination IATA code.

    Returns
    -------
    dict
        {
            'available': bool,
            'count': int,           # number of matching route records
            'message': str,         # human‑readable summary
            'suggestions': list[str] # optional suggestions for alternatives
        }
    """
    # Resolve to internal IDs
    try:
        ac_id = mapping.resolve_aircraft(aircraft)  # returns shortname, but we need internal id? Actually resolve_aircraft returns shortname.
        # We need the internal aircraft id (fd). Let's get from dataset.
        ac_row = dataset_service.get_aircraft_by_name(aircraft)
        if ac_row is None:
            raise ValueError(f"Aircraft '{aircraft}' not found")
        fd = int(ac_row['id'])
        jd = mapping.resolve_airport(origin_iata)   # origin airport id
        yd = mapping.resolve_airport(dest_iata)     # destination airport id
    except ValueError as e:
        return {
            'available': False,
            'count': 0,
            'message': str(e),
            'suggestions': []
        }

    # Load routes and filter
    routes = dataset_service.routes
    mask = (routes['fd'] == fd) & (routes['jd'] == jd) & (routes['yd'] == yd)
    matching = routes[mask]
    count = len(matching)

    if count > 0:
        return {
            'available': True,
            'count': count,
            'message': f'Found {count} matching route records.',
            'suggestions': []
        }
    else:
        # Generate suggestions: same aircraft with different origins/destinations?
        # For simplicity, we can show some alternative origins and destinations for this aircraft.
        # Get all routes for this aircraft
        ac_routes = dataset_service.routes[dataset_service.routes['fd'] == fd]
        if len(ac_routes) > 0:
            # Get unique origin and destination ids
            origin_ids = ac_routes['jd'].unique()
            dest_ids = ac_routes['yd'].unique()
            # Convert to IATA codes (limit to a few)
            orig_iatas = []
            dest_iatas = []
            for oid in origin_ids[:10]:
                ap = dataset_service.airports[dataset_service.airports['id'] == oid]
                if not ap.empty:
                    orig_iatas.append(ap.iloc[0]['iata'])
            for did in dest_ids[:10]:
                ap = dataset_service.airports[dataset_service.airports['id'] == did]
                if not ap.empty:
                    dest_iatas.append(ap.iloc[0]['iata'])
            suggestions = []
            if orig_iatas:
                suggestions.append(f"Try same aircraft with origins: {', '.join(orig_iatas)}")
            if dest_iatas:
                suggestions.append(f"   or destinations: {', '.join(dest_iatas)}")
            # Also suggest other popular aircraft on this route? Could be heavy.
            # We'll keep it simple.
        else:
            suggestions = [f"No routes found for aircraft '{aircraft}'. Try a different aircraft."]
        return {
            'available': False,
            'count': 0,
            'message': f'This route‑aircraft combination is not available in the dataset.',
            'suggestions': suggestions
        }


def format_availability_message(
    aircraft: str,
    origin_iata: str,
    dest_iata: str,
) -> str:
    """
    Return a human‑readable message about route availability.
    Mirrors the output of check_route_availability but formatted as a single line.
    """
    res = check_route_availability(aircraft, origin_iata, dest_iata)
    if res['available']:
        return f"Route available: {res['count']} record(s) found."
    else:
        # Build message similar to the example
        msg = f"This route‑aircraft combination is not available in the dataset."
        if res['suggestions']:
            msg += " " + " ".join(res['suggestions'])
        return msg


def compute_upgrade_economics(
    current_ac: str,
    target_ac: str,
    origin_iata: str,
    dest_iata: str,
    seat_config_current: Dict[str, int],
    seat_config_target: Dict[str, int],
    assumptions: Optional[Dict[str, Any]] = None,
    ticket_price_mode: str = "easy",
    ticket_price_optimal: bool = True,
    current_qty: int = 1,
    target_qty: int = 1,
) -> Dict[str, Any]:
    """
    Evaluate the economic impact of upgrading from `current_ac` to `target_ac`.

    Returns a dictionary containing:
    - profit_per_flight for each aircraft
    - profit_per_year for each aircraft (scaled by quantity)
    - additional_investment (difference in acquisition cost)
    - additional_yearly_profit
    - ROI (as a decimal, e.g., 0.25 for 25%)
    - payback_period_years (in years, or float('inf') if not applicable)
    """
    # Get per‑flight economics for both options
    cur = compute_flight_economics(
        current_ac,
        origin_iata,
        dest_iata,
        seat_config_current,
        assumptions,
        ticket_price_mode,
        ticket_price_optimal,
    )
    tgt = compute_flight_economics(
        target_ac,
        origin_iata,
        dest_iata,
        seat_config_target,
        assumptions,
        ticket_price_mode,
        ticket_price_optimal,
    )

    # Acquisition cost (purchase price) from aircraft data
    cur_ac_row = dataset_service.get_aircraft_by_name(current_ac)
    tgt_ac_row = dataset_service.get_aircraft_by_name(target_ac)
    if cur_ac_row is None:
        raise ValueError(f"Current aircraft '{current_ac}' not found")
    if tgt_ac_row is None:
        raise ValueError(f"Target aircraft '{target_ac}' not found")

    cur_cost_per_ac = float(cur_ac_row.get("cost", 0.0))
    tgt_cost_per_ac = float(tgt_ac_row.get("cost", 0.0))

    # ------------------------------------------------------------------
    # Financial calculations
    # ------------------------------------------------------------------
    profit_per_flight_cur = cur["profit"]
    profit_per_flight_tgt = tgt["profit"]

    # Yearly profit per aircraft (already includes flights/day & days/year)
    profit_per_year_cur = cur["profit_per_year"]
    profit_per_year_tgt = tgt["profit_per_year"]

    # Scale by quantity
    total_yearly_profit_cur = profit_per_year_cur * current_qty
    total_yearly_profit_tgt = profit_per_year_tgt * target_qty

    # Investment: total acquisition cost
    total_cur_investment = cur_cost_per_ac * current_qty
    total_tgt_investment = tgt_cost_per_ac * target_qty
    additional_investment = total_tgt_investment - total_cur_investment

    # Profit change
    additional_yearly_profit = total_yearly_profit_tgt - total_yearly_profit_cur

    if additional_yearly_profit != 0:
        if additional_investment > 0:
            roi = additional_yearly_profit / additional_investment
            payback_years = additional_investment / additional_yearly_profit
        else:
            # Negative investment (i.e., selling down) -> immediate profit
            roi = float("inf")
            payback_years = 0.0
    else:
        roi = 0.0
        payback_years = float("inf")

    return {
        "current_aircraft": cur["aircraft"],
        "target_aircraft": tgt["aircraft"],
        "profit_per_flight_current": profit_per_flight_cur,
        "profit_per_flight_target": profit_per_flight_tgt,
        "profit_per_year_current": profit_per_year_cur,
        "profit_per_year_target": profit_per_year_tgt,
        "total_yearly_profit_current": total_yearly_profit_cur,
        "total_yearly_profit_target": total_yearly_profit_tgt,
        "additional_investment": additional_investment,
        "additional_yearly_profit": additional_yearly_profit,
        "roi": roi,
        "payback_period_years": payback_years,
        "assumptions_used": cur["assumptions_used"],
        "fuel_price_used": cur["fuel_price_used"],
        "co2_price_used": cur["co2_price_used"],
    }


def advise_upgrade(
    current_ac: str,
    target_ac: str,
    origin_iata: str,
    dest_iata: str,
    seat_config_current: Dict[str, int],
    seat_config_target: Dict[str, int],
    assumptions: Optional[Dict[str, Any]] = None,
    ticket_price_mode: str = "easy",
    ticket_price_optimal: bool = True,
    current_qty: int = 1,
    target_qty: int = 1,
) -> Dict[str, Any]:
    """
    Advise on whether upgrading from `current_ac` to `target_ac` is worthwhile.

    Wrapper around compute_upgrade_economics that adds a human‑readable advice
    string based on the ROI and payback period.

    Returns the same dictionary as compute_upgrade_economics with an extra
    'advice' key.
    """
    result = compute_upgrade_economics(
        current_ac=current_ac,
        target_ac=target_ac,
        origin_iata=origin_iata,
        dest_iata=dest_iata,
        seat_config_current=seat_config_current,
        seat_config_target=seat_config_target,
        assumptions=assumptions,
        ticket_price_mode=ticket_price_mode,
        ticket_price_optimal=ticket_price_optimal,
        current_qty=current_qty,
        target_qty=target_qty,
    )
    # Generate advice
    roi = result.get('roi', 0.0)
    payback = result.get('payback_period_years', float('inf'))
    additional_investment = result.get('additional_investment', 0.0)
    additional_yearly_profit = result.get('additional_yearly_profit', 0.0)

    if additional_yearly_profit <= 0:
        advice = "Not profitable: upgrade would not increase yearly profit."
    elif additional_investment <= 0:
        advice = "Profitable: upgrade reduces cost (negative investment). Consider doing it."
    else:
        if roi > 0.2:  # arbitrary threshold
            advice = f"Profitable upgrade with ROI {roi*100:.1f}% and payback {payback:.1f} years. Recommended."
        elif roi > 0:
            advice = f"Marginally profitable: ROI {roi*100:.1f}%, payback {payback:.1f} years. Consider if other factors favor upgrade."
        else:
            advice = "Upgrade not profitable (negative ROI)."
    result['advice'] = advice
    return result