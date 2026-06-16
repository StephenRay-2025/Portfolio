"""
Streamlit UI for Aircraft Lifecycle Analyzer.
"""
import streamlit as st
import sys
import os

# Add the analysis directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
from lifecycle import lifecycle_analysis
from datasets import dataset_service
st.set_page_config(page_title="AM4 Aircraft Lifecycle Analyzer", layout="centered")
from economics import compute_flight_economics, _get_assumptions
from pricing import calculate_ticket_price

st.title("✈️ Aircraft Lifecycle Analyzer (AM4)")
st.caption("Analyze profit, cost, fuel, and CO2 for aircraft upgrade decisions.")

with st.form("analysis_form"):
    st.subheader("Fleet Configuration")
    col1, col2 = st.columns(2)
    with col1:
        current_ac = st.text_input("Current Aircraft (shortname, e.g., A220-100)", value="A220-100")
        current_qty = st.number_input("Current Quantity", min_value=1, value=2, step=1)
    with col2:
        target_ac = st.text_input("Target Aircraft (shortname, e.g., A320neo)", value="a32neo")
        target_qty = st.number_input("Target Quantity to Add", min_value=1, value=1, step=1)
    
    st.subheader("Route")
    col3, col4 = st.columns(2)
    with col3:
        origin_iata = st.text_input("Origin IATA (e.g., PEK)", value="PEK").upper()
    with col4:
        dest_iata = st.text_input("Destination IATA (e.g., SIN)", value="SIN").upper()
    
    st.subheader("Assumptions")
    flights_per_day = st.number_input("Flights per Day per Aircraft", min_value=1, value=2, step=1)
    days_per_year = st.number_input("Days per Year", min_value=1, value=365, step=1)
    
    submitted = st.form_submit_button("Analyze")

if submitted:
    with st.spinner("Running analysis..."):
        try:
            result = lifecycle_analysis(
                current_ac=current_ac,
                current_qty=int(current_qty),
                target_ac=target_ac,
                target_qty=int(target_qty),
                origin_iata=origin_iata,
                dest_iata=dest_iata,
                flights_per_day=int(flights_per_day),
                days_per_year=int(days_per_year)
            )
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    
    if 'error' in result:
        st.error(result['error'])
    else:
        st.success("Analysis Complete")
        st.subheader("Results")
        st.write(f"**Route:** {result['route']} (distance: {result['distance_km']:.0f} km)")
        st.write(f"**Current Aircraft:** {result['current_aircraft']} (×{current_qty})")
        st.write(f"**Target Aircraft:** {result['target_aircraft']} (×{target_qty})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Profit per Flight (Current)", f"{result['profit_per_flight_current']:,.0f}")
            st.metric("Profit per Year (Current)", f"{result['profit_per_year_current']:,.0f}")
        with col2:
            st.metric("Profit per Flight (Target)", f"{result['profit_per_flight_target']:,.0f}")
            st.metric("Profit per Year (Target)", f"{result['profit_per_year_target']:,.0f}")
        
        st.write(f"**Additional Investment:** {result['additional_investment']:,.0f}")
        st.write(f"**Additional Yearly Profit:** {result['additional_yearly_profit']:,.0f}")
        if result['payback_years'] == float('inf'):
            st.write("**Payback Period:** ∞ (no additional profit)")
        else:
            st.write(f"**Payback Period:** {result['payback_years']:.1f} years")
        
        with st.expander("Environmental Impact"):
            st.write(f"Fuel per Flight - Current: {result['fuel_per_flight_current_kg']:.1f} kg")
            st.write(f"Fuel per Flight - Target: {result['fuel_per_flight_target_kg']:.1f} kg")
            st.write(f"CO₂ per Flight - Current: {result['co2_per_flight_current_kg']:.1f} kg")
            st.write(f"CO₂ per Flight - Target: {result['co2_per_flight_target_kg']:.1f} kg")
        
        st.caption("Note: Profit values are derived from the AM4 route.parquet 'd' field, interpreted as profit per flight. Actual profitability depends on many factors; this is a simplified illustrative model.")    # Show profit source
    st.caption("Profit source for current aircraft: " + str(result.get('profit_source_current', 'unknown')))
    st.caption("Profit source for target aircraft: " + str(result.get('profit_source_target', 'unknown')))

    






    # Flight Detail Card
    with st.expander("✈️ Flight Detail Card", expanded=True):
        try:
                ori_row = dataset_service.get_airport_by_code(origin_iata.upper())
                dest_row = dataset_service.get_airport_by_code(dest_iata.upper())
        except Exception as e:
                st.warning(f"Error fetching airports: {e}")
                ori_row = None
                dest_row = None
        if ori_row is None or dest_row is None:
                st.warning("Origin or destination airport not found")
                # Set defaults
                route_distance_km = 0.0
                ticket_Y = ticket_J = ticket_F = 0.0
                daily_demand = 0.0
        else:
                        # Compute route distance and basic info
                        try:
                                from math import radians, sin, cos, sqrt, atan2
                                def haversine(lat1, lon1, lat2, lon2):
                                        R = 6371.0
                                        phi1 = radians(lat1)
                                        phi2 = radians(lat2)
                                        dphi = radians(lat2 - lat1)
                                        dlambda = radians(lon2 - lon1)
                                        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
                                        c = 2 * atan2(sqrt(a), sqrt(1-a))
                                        return R * c
                                route_distance_km = haversine(float(ori_row["lat"]), float(ori_row["lng"]),
                                float(dest_row["lat"]), float(dest_row["lng"]))
                        except Exception as e:
                                st.warning(f"Error computing route distance: {e}")
                                route_distance_km = 0.0
        ticket_Y = calculate_ticket_price(route_distance_km, "Y")
        ticket_J = calculate_ticket_price(route_distance_km, "J")
        ticket_F = calculate_ticket_price(route_distance_km, "F")
        daily_demand = float(ori_row.get("market", 0.0))
        route_table = [
                {"Metric": "Route Length (km)", "Value": f"{route_distance_km:,.0f}"},
                {"Metric": "Route Opening Fee", "Value": "N/A"},
                {"Metric": "Daily Demand (flights)", "Value": f"{daily_demand:,.0f}"},
                {"Metric": "Y Ticket Price", "Value": f"{ticket_Y:,.0f}"},
                {"Metric": "J Ticket Price", "Value": f"{ticket_J:,.0f}"},
                {"Metric": "F Ticket Price", "Value": f"{ticket_F:,.0f}"},
        ]
        st.subheader("🛣️ Route Data")
        st.table(route_table)
        for label, ac_name, qty in [("Current", current_ac, int(current_qty)), ("Target", target_ac, int(target_qty))]:
                try:
                        ac_row = dataset_service.get_aircraft_by_name(ac_name)
                        if ac_row is None:
                                st.warning(f"Aircraft {ac_name} not found")
                                continue
                except Exception as e:
                        st.warning(f"Error fetching aircraft {ac_name}: {e}")
                        continue
                purchase_price = float(ac_row.get("cost", 0.0))
                capacity = int(ac_row.get("capacity", 0))
                range_km = float(ac_row.get("range", 0.0))
                engine = ac_row.get("ename", "Unknown")
                fuel_per_hour = float(ac_row.get("fuel", 0.0))
                co2_per_hour = float(ac_row.get("co2", 0.0))
                maint_hours = float(ac_row.get("maint", 0.0))
                a_check_hours = maint_hours  # placeholder
                pilots = int(ac_row.get("pilots", 0))
                cabin_crew = int(ac_row.get("crew", 0)) - pilots
                engineers = int(ac_row.get("engineers", 0))
                technicians = int(ac_row.get("technicians", 0))
                speed_kmh = float(ac_row.get("speed", 0.0))
                flight_time_hr = route_distance_km / speed_kmh if speed_kmh > 0 else float("inf")
                fuel_per_flight_lbs = fuel_per_hour * flight_time_hr
                co2_per_flight_lbs = co2_per_hour * flight_time_hr
                co2_per_flight_kg = co2_per_flight_lbs * 0.453592
                profit_per_flight = result.get(f"profit_per_flight_{label.lower()}", 0.0)
                assumptions = _get_assumptions()
                LF = assumptions["load_factor"]
                flights_per_day = daily_demand / (capacity * LF) if capacity * LF > 0 else 0.0
                profit_per_day = profit_per_flight * flights_per_day
                profit_per_week = profit_per_day * 7
                profit_per_month = profit_per_day * 30
                profit_per_year = profit_per_day * 365
                additional_investment = result.get("additional_investment", 0.0)
                additional_yearly_profit = result.get("additional_yearly_profit", 0.0)
                if additional_yearly_profit > 0:
                        payback_hours = (additional_investment / additional_yearly_profit) * 8760
                else:
                        payback_hours = float("inf")
        spec_table = [
                {"Metric": "Aircraft Model", "Value": ac_row.get("shortname", ac_name)},
                {"Metric": "Purchase Price", "Value": f"{purchase_price:,.0f}"},
                {"Metric": "Seats", "Value": f"{capacity}"},
                {"Metric": "Range (km)", "Value": f"{range_km:,.0f}"},
                {"Metric": "Engine", "Value": engine},
                {"Metric": "Fuel/hr (lb)", "Value": f"{fuel_per_hour:.2f}"},
                {"Metric": "Speed (km/h)", "Value": f"{speed_kmh:.0f}"},
                {"Metric": "Maintenance (h)", "Value": f"{maint_hours:.1f}"},
                {"Metric": "A‑Check (h)", "Value": f"{a_check_hours:.1f}"},
                {"Metric": "Pilots", "Value": f"{pilots}"},
                {"Metric": "Cabin Crew", "Value": f"{cabin_crew}"},
                {"Metric": "Engineers", "Value": f"{engineers}"},
                {"Metric": "Technicians", "Value": f"{technicians}"},
                {"Metric": "Flight Time (h)", "Value": f"{flight_time_hr:.1f}"},
                {"Metric": "Fuel per Flight (lb)", "Value": f"{fuel_per_flight_lbs:.0f}"},
                {"Metric": "CO₂ per Flight (kg)", "Value": f"{co2_per_flight_kg:.0f}"},
                {"Metric": "Profit per Flight", "Value": f"{profit_per_flight:,.0f}"},
                {"Metric": "Profit per Day", "Value": f"{profit_per_day:,.0f}"},
                {"Metric": "Profit per Week", "Value": f"{profit_per_week:,.0f}"},
                {"Metric": "Profit per Month", "Value": f"{profit_per_month:,.0f}"},
                {"Metric": "Profit per Year", "Value": f"{profit_per_year:,.0f}"},
                {"Metric": "Payback Period (h)", "Value": f"{payback_hours:.1f}" if payback_hours!=float("inf") else "∞"},
        ]
        st.subheader(f"✈️ {label} Aircraft ({ac_name}) ×{qty}")
        st.table(spec_table)
        st.markdown("---")
    with st.expander("✈️ Flight Detail Card", expanded=True):
        try:
                    ori_row = dataset_service.get_airport_by_code(origin_iata.upper())
                    dest_row = dataset_service.get_airport_by_code(dest_iata.upper())
        except Exception as e:
                    st.warning(f"Error fetching airports: {e}")
                    ori_row = None
                    dest_row = None
        if ori_row is None or dest_row is None:
                    st.warning("Origin or destination airport not found")
                    # Set defaults to avoid errors
                    route_distance_km = 0.0
                    ticket_Y = ticket_J = ticket_F = 0.0
                    daily_demand = 0.0
        else:
                    # Compute route distance and basic info
                            try:
                                from math import radians, sin, cos, sqrt, atan2
                                def haversine(lat1, lon1, lat2, lon2):
                                            R = 6371.0
                                            phi1 = radians(lat1)
                                            phi2 = radians(lat2)
                                            dphi = radians(lat2 - lat1)
                                            dlambda = radians(lon2 - lon1)
                                            a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
                                            c = 2 * atan2(sqrt(a), sqrt(1-a))
                                            return R * c
                                route_distance_km = haversine(float(ori_row["lat"]), float(ori_row["lng"]),
                                                           float(dest_row["lat"]), float(dest_row["lng"]))
                            except Exception as e:
                                st.warning(f"Error computing route distance: {e}")
                                route_distance_km = 0.0
                    ticket_Y = calculate_ticket_price(route_distance_km, "Y")
                    ticket_J = calculate_ticket_price(route_distance_km, "J")
                    ticket_F = calculate_ticket_price(route_distance_km, "F")
                    daily_demand = float(ori_row.get("market", 0.0))
                    route_table = [
                        {"Metric": "Route Length (km)", "Value": f"{route_distance_km:,.0f}"},
                        {"Metric": "Route Opening Fee", "Value": "N/A"},
                        {"Metric": "Daily Demand (flights)", "Value": f"{daily_demand:,.0f}"},
                        {"Metric": "Y Ticket Price", "Value": f"{ticket_Y:,.0f}"},
                        {"Metric": "J Ticket Price", "Value": f"{ticket_J:,.0f}"},
                        {"Metric": "F Ticket Price", "Value": f"{ticket_F:,.0f}"},
                    ]
                    st.subheader("🛣️ Route Data")
                    st.table(route_table)
            for label, ac_name, qty in [("Current", current_ac, int(current_qty)), ("Target", target_ac, int(target_qty))]:
                        try:
                                    ac_row = dataset_service.get_aircraft_by_name(ac_name)
                                    if ac_row is None:
                                                st.warning(f"Aircraft {ac_name} not found")
                                                continue
                        except Exception as e:
                                    st.warning(f"Error fetching aircraft {ac_name}: {e}")
                                    continue
                        purchase_price = float(ac_row.get("cost", 0.0))
                        capacity = int(ac_row.get("capacity", 0))
                        range_km = float(ac_row.get("range", 0.0))
                        engine = ac_row.get("ename", "Unknown")
                        fuel_per_hour = float(ac_row.get("fuel", 0.0))
                        co2_per_hour = float(ac_row.get("co2", 0.0))
                        maint_hours = float(ac_row.get("maint", 0.0))
                        a_check_hours = maint_hours  # placeholder
                        pilots = int(ac_row.get("pilots", 0))
                        cabin_crew = int(ac_row.get("crew", 0)) - pilots
                        engineers = int(ac_row.get("engineers", 0))
                        technicians = int(ac_row.get("technicians", 0))
                        speed_kmh = float(ac_row.get("speed", 0.0))
                        flight_time_hr = route_distance_km / speed_kmh if speed_kmh > 0 else float('inf')
                        fuel_per_flight_lbs = fuel_per_hour * flight_time_hr
                        co2_per_flight_lbs = co2_per_hour * flight_time_hr
                        co2_per_flight_kg = co2_per_flight_lbs * 0.453592
                        profit_per_flight = result.get(f'profit_per_flight_{label.lower()}', 0.0)
                        assumptions = _get_assumptions()
                        LF = assumptions["load_factor"]
                        flights_per_day = daily_demand / (capacity * LF) if capacity * LF > 0 else 0.0
                        profit_per_day = profit_per_flight * flights_per_day
                        profit_per_week = profit_per_day * 7
                        profit_per_month = profit_per_day * 30
                        profit_per_year = profit_per_day * 365
                        additional_investment = result.get('additional_investment', 0.0)
                        additional_yearly_profit = result.get('additional_yearly_profit', 0.0)
                        if additional_yearly_profit > 0:
                                    payback_hours = (additional_investment / additional_yearly_profit) * 8760
                        else:
                                    payback_hours = float('inf')
                        spec_table = [
                            {"Metric": "Aircraft Model", "Value": ac_row.get("shortname", ac_name)},
                            {"Metric": "Purchase Price", "Value": f"{purchase_price:,.0f}"},
                            {"Metric": "Seats", "Value": f"{capacity}"},
                            {"Metric": "Range (km)", "Value": f"{range_km:,.0f}"},
                            {"Metric": "Engine", "Value": engine},
                            {"Metric": "Fuel/hr (lb)", "Value": f"{fuel_per_hour:.2f}"},
                            {"Metric": "Speed (km/h)", "Value": f"{speed_kmh:.0f}"},
                            {"Metric": "Maintenance (h)", "Value": f"{maint_hours:.1f}"},
                            {"Metric": "A‑Check (h)", "Value": f"{a_check_hours:.1f}"},
                            {"Metric": "Pilots", "Value": f"{pilots}"},
                            {"Metric": "Cabin Crew", "Value": f"{cabin_crew}"},
                            {"Metric": "Engineers", "Value": f"{engineers}"},
                            {"Metric": "Technicians", "Value": f"{technicians}"},
                            {"Metric": "Flight Time (h)", "Value": f"{flight_time_hr:.1f}"},
                            {"Metric": "Fuel per Flight (lb)", "Value": f"{fuel_per_flight_lbs:.0f}"},
                            {"Metric": "CO₂ per Flight (kg)", "Value": f"{co2_per_flight_kg:.0f}"},
                            {"Metric": "Profit per Flight", "Value": f"{profit_per_flight:,.0f}"},
                            {"Metric": "Profit per Day", "Value": f"{profit_per_day:,.0f}"},
                            {"Metric": "Profit per Week", "Value": f"{profit_per_week:,.0f}"},
                            {"Metric": "Profit per Month", "Value": f"{profit_per_month:,.0f}"},
                            {"Metric": "Profit per Year", "Value": f"{profit_per_year:,.0f}"},
                            {"Metric": "Payback Period (h)", "Value": f"{payback_hours:.1f}" if payback_hours!=float('inf') else "∞"},
                        ]
                        st.subheader(f"✈️ {label} Aircraft ({ac_name}) ×{qty}")
                        st.table(spec_table)
                        st.markdown('---')
