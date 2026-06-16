#!/usr/bin/env python3
"""
Demonstration of the AM4 Economics Engine.

Shows how to use the pricing and economics modules to compute:
- distance, flight time
- ticket prices for Y, J, F
- revenue, fuel cost, CO2 cost, profit
- daily and yearly profit
- upgrade advice with payback period
"""

import sys
sys.path.insert(0, '.')

from analysis import pricing, economics, mapping, datasets

def main():
    print("=== AM4 Economics Engine Demo ===\n")
    
    # Example inputs
    aircraft_ui = "A220-100"
    origin_iata = "PEK"
    dest_iata = "SIN"
    # Seat configuration: all economy
    ac_row = datasets.dataset_service.get_aircraft_by_name(aircraft_ui)
    if ac_row is None:
        print(f"Aircraft {aircraft_ui} not found")
        return
    capacity = int(ac_row.get("capacity", 0))
    seat_config = {"Y": capacity, "J": 0, "F": 0}
    
    print(f"Aircraft: {aircraft_ui} (shortname: {ac_row.get('shortname')})")
    print(f"Route: {origin_iata} -> {dest_iata}")
    print(f"Seat config: {seat_config}\n")
    
    # 1. Distance and flight time (via economics function)
    flight_res = economics.compute_flight_economics(
        aircraft_shortname=aircraft_ui,
        origin_iata=origin_iata,
        dest_iata=dest_iata,
        seat_config=seat_config,
    )
    print("--- Flight Economics ---")
    print(f"Distance: {flight_res['distance_km']:.2f} km")
    print(f"Flight time: {flight_res['flight_time_hr']:.2f} h")
    # Ticket prices per class (using pricing directly)
    distance = flight_res['distance_km']
    ticket_Y = pricing.calculate_ticket_price(distance, "Y", mode="easy", optimal=True)
    ticket_J = pricing.calculate_ticket_price(distance, "J", mode="easy", optimal=True)
    ticket_F = pricing.calculate_ticket_price(distance, "F", mode="easy", optimal=True)
    print(f"Ticket price (Y): {ticket_Y:.2f}")
    print(f"Ticket price (J): {ticket_J:.2f}")
    print(f"Ticket price (F): {ticket_F:.2f}")
    print(f"Revenue: {flight_res['revenue']:.2f}")
    print(f"Fuel cost: {flight_res['fuel_cost']:.2f}")
    print(f"CO2 cost: {flight_res['co2_cost']:.2f}")
    print(f"Profit per flight: {flight_res['profit']:.2f}")
    print(f"Profit per day: {flight_res['profit_per_day']:.2f}")
    print(f"Profit per year: {flight_res['profit_per_year']:.2f}\n")
    
    # 2. Route availability
    avail = economics.check_route_availability(aircraft_ui, origin_iata, dest_iata)
    print("--- Route Availability ---")
    print(economics.format_availability_message(aircraft_ui, origin_iata, dest_iata))
    if avail['suggestions']:
        print("Suggestions:")
        for s in avail['suggestions'][:3]:
            print("  -", s)
    print()
    
    # 3. Upgrade example: to A320neo (shortname a32neo)
    target_ac = "a32neo"
    target_row = datasets.dataset_service.get_aircraft_by_name(target_ac)
    if target_row is None:
        # try alternative
        target_row = datasets.dataset_service.get_aircraft_by_name("A320-NEO")
        if target_row is None:
            print(f"Target aircraft {target_ac} not found")
            return
    target_capacity = int(target_row.get("capacity", 0))
    seat_config_target = {"Y": target_capacity, "J": 0, "F": 0}
    print(f"--- Upgrade Analysis: {aircraft_ui} -> {target_row.get('shortname')} ---")
    up = economics.advise_upgrade(
        current_ac=aircraft_ui,
        target_ac=target_row.get('shortname'),
        origin_iata=origin_iata,
        dest_iata=dest_iata,
        seat_config_current=seat_config,
        seat_config_target=seat_config_target,
    )
    print(f"Advice: {up['advice']}")
    print(f"ROI: {up['roi']*100:.1f}%")
    print(f"Payback period: {up['payback_period_years']:.2f} years")
    print(f"Additional yearly profit: {up['additional_yearly_profit']:.2f}")
    print(f"Additional investment: {up['additional_investment']:.2f}")

if __name__ == "__main__":
    main()