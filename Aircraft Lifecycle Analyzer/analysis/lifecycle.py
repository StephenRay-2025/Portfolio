"""Aircraft Lifecycle Analyzer for AM4user project.
Uses DatasetService to access Parquet data.
Provides functions to compute profit, cost, fuel, CO2 for a given aircraft on a given route.
"""
import math
from datasets import dataset_service
import mapping
from economics import compute_flight_economics

def haversine(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in kilometers."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_aircraft_info(shortname):
    """Return aircraft row matching shortname (e.g., 'A220-100')."""
    ac = dataset_service.get_aircraft_by_name(shortname)
    if ac is None:
        raise ValueError(f"Aircraft shortname '{shortname}' not found")
    return ac

def get_airport_info(iata):
    """Return airport row matching IATA code."""
    ap = dataset_service.get_airport_by_code(iata)
    if ap is None:
        raise ValueError(f"Airport IATA '{iata}' not found")
    return ap

def get_route_profit(aircraft_id: int, origin_id: int, dest_id: int):
    """
    Look up profit-per-flight for (aircraft, origin, dest) in route.parquet.
    If not present, compute it on the fly using the aircraft's specs and
    the great-circle distance between the two airports.

    Returns
    -------
    profit : float
        Profit per flight (currency unit).
    from_db : bool
        True if the value was read from route.parquet,
        False if it was calculated just now.
    """
    from economics import compute_flight_economics
    import mapping

    # ---- 1. Try the DB first -------------------------------------------------
    df = dataset_service.find_routes(
        aircraft_id=aircraft_id,
        origin_id=origin_id,
        dest_id=dest_id
    )
    if not df.empty:
        return float(df.iloc[0]["d"]), True

    # ---- 2. Not in DB – we need to compute it --------------------------------
    # Resolve the UI strings back to objects we already have IDs for.
    # (We already have the IDs, but we need the full rows for speed/fuel/etc.)
    ac_row = dataset_service.get_aircraft_by_id(aircraft_id)
    ori_row = dataset_service.get_airport_by_id(origin_id)
    dest_row = dataset_service.get_airport_by_id(dest_id)

    if ac_row is None or ori_row is None or dest_row is None:
        raise ValueError(
            f"Missing reference data for aircraft_id={aircraft_id}, "
            f"origin_id={origin_id}, dest_id={dest_id}"
        )

    # Build a minimal seat‑config – the lifecycle UI does not expose seat
    # configuration, so we use a generic all‑economy layout derived from
    # the aircraft’s capacity.
    capacity = int(ac_row.get("capacity", 0))
    seat_config = {"Y": capacity, "J": 0, "F": 0}   # all economy

    # Re‑use the existing economics function – it already does:
    #   * haversine distance
    #   * live fuel/CO₂ pricing
    #   * revenue – cost = profit
    econ = compute_flight_economics(
        aircraft_shortname=ac_row.get("shortname", "UNKNOWN"),
        origin_iata=ori_row.get("iata", "???"),
        dest_iata=dest_row.get("iata", "???"),
        seat_config=seat_config,
        # Use the default assumptions (they are already inside compute_flight_economics)
    )
    profit = econ.get("profit")
    if profit is None:
        raise RuntimeError("Failed to compute profit from economics model.")
    return profit, False

def get_aircraft_speed(aircraft_row):
    """Speed in km/h."""
    return float(aircraft_row['speed'])

def get_aircraft_fuel_per_hour(aircraft_row):
    """Fuel consumption per hour (units? maybe kg/h)."""
    return float(aircraft_row['fuel'])

def get_aircraft_co2_per_hour(aircraft_row):
    """CO2 emission per hour (kg/h?)."""
    return float(aircraft_row['co2'])

def get_aircraft_cost(aircraft_row):
    """Purchase price (currency)."""
    return float(aircraft_row['cost'])

def compute_route_metrics(aircraft_shortname, origin_iata, dest_iata):
    """
    Compute profit, flight time, fuel consumption, CO2 for a given aircraft on a route.
    Returns dict with keys: profit_per_flight, flight_time_hr, fuel_per_flight, co2_per_flight, distance_km, profit_source
    """
    # Resolve UI inputs to internal IDs using mapping layer
    try:
        # aircraft_shortname may be name or shortname; mapping returns internal shortname
        _ = mapping.resolve_aircraft(aircraft_shortname)  # validate
    except ValueError as e:
        raise ValueError(f"Invalid aircraft: {e}")
    try:
        origin_id = mapping.resolve_airport(origin_iata)
        dest_id = mapping.resolve_airport(dest_iata)
    except ValueError as e:
        raise ValueError(f"Invalid airport: {e}")
    
    # Fetch aircraft row for attributes (name, cost, speed, fuel, co2)
    ac = dataset_service.get_aircraft_by_name(aircraft_shortname)
    if ac is None:
        raise ValueError(f"Aircraft '{aircraft_shortname}' not found")
    # Fetch airport rows for lat/lng and IATA
    ori = dataset_service.get_airport_by_code(origin_iata.upper())
    dest = dataset_service.get_airport_by_code(dest_iata.upper())
    if ori is None or dest is None:
        raise ValueError(f"Airport not found for IATA {origin_iata} or {dest_iata}")
    
    ac_id = int(ac['id'])
    # ori_id and dest_id already resolved
    
    profit, from_db = get_route_profit(ac_id, origin_id, dest_id)
    profit_source = "db" if from_db else "computed"
    
    speed = get_aircraft_speed(ac)
    distance = haversine(ori['lat'], ori['lng'], dest['lat'], dest['lng'])
    flight_time = distance / speed if speed > 0 else float('inf')
    
    fuel_per_hour = get_aircraft_fuel_per_hour(ac)
    fuel_per_flight = fuel_per_hour * flight_time
    
    co2_per_hour = get_aircraft_co2_per_hour(ac)
    co2_per_flight = co2_per_hour * flight_time
    
    return {
        'profit_per_flight': profit,
        'distance_km': distance,
        'flight_time_hr': flight_time,
        'fuel_per_flight_kg': fuel_per_flight,
        'co2_per_flight_kg': co2_per_flight,
        'aircraft_cost': get_aircraft_cost(ac),
        'aircraft_shortname': ac['shortname'],
        'aircraft_name': ac['name'],
        'origin': ori['iata'],
        'destination': dest['iata'],
        'profit_source': profit_source
    }

def lifecycle_analysis(current_ac, current_qty, target_ac, target_qty, origin_iata, dest_iata, flights_per_day=1, days_per_year=365):
    """
    Simple lifecycle analysis.
    current_ac: shortname of current aircraft in fleet
    current_qty: number of such aircraft
    target_ac: shortname of new aircraft to consider
    target_qty: number of target aircraft to acquire
    origin_iata, dest_iata: route to evaluate
    flights_per_day: average flights per day per aircraft (utilization)
    Returns dict with summary.
    """
    # Get metrics for current and target aircraft on the route
    try:
        curr_metrics = compute_route_metrics(current_ac, origin_iata, dest_iata)
    except ValueError as e:
        return {'error': f'Current aircraft metrics: {e}'}
    try:
        targ_metrics = compute_route_metrics(target_ac, origin_iata, dest_iata)
    except ValueError as e:
        return {'error': f'Target aircraft metrics: {e}'}
    
    # Extract IDs and profit source for UI
    origin_id = mapping.resolve_airport(origin_iata)
    dest_id = mapping.resolve_airport(dest_iata)
    cur_ac = dataset_service.get_aircraft_by_name(current_ac)
    tgt_ac = dataset_service.get_aircraft_by_name(target_ac)
    cur_ac_id = int(cur_ac['id'])
    tgt_ac_id = int(tgt_ac['id'])
    
    # Profit per year
    profit_per_flight_curr = curr_metrics['profit_per_flight']
    profit_per_flight_targ = targ_metrics['profit_per_flight']
    
    yearly_flights_per_ac = flights_per_day * days_per_year
    profit_year_curr = profit_per_flight_curr * yearly_flights_per_ac * current_qty
    profit_year_targ = profit_per_flight_targ * yearly_flights_per_ac * target_qty
    
    # Capital cost
    capital_cost_curr = curr_metrics['aircraft_cost'] * current_qty
    capital_cost_targ = targ_metrics['aircraft_cost'] * target_qty
    
    # Simple payback period for additional investment if we switch
    additional_investment = capital_cost_targ - capital_cost_curr
    additional_yearly_profit = profit_year_targ - profit_year_curr
    if additional_yearly_profit != 0:
        payback_years = additional_investment / additional_yearly_profit if additional_investment > 0 else float('inf')
    else:
        payback_years = float('inf')
    
    return {
        'current_aircraft': curr_metrics['aircraft_name'],
        'target_aircraft': targ_metrics['aircraft_name'],
        'route': f"{curr_metrics['origin']} -> {curr_metrics['destination']}",
        'distance_km': curr_metrics['distance_km'],
        'profit_per_flight_current': profit_per_flight_curr,
        'profit_per_flight_target': profit_per_flight_targ,
        'profit_per_year_current': profit_year_curr,
        'profit_per_year_target': profit_year_targ,
        'capital_cost_current': capital_cost_curr,
        'capital_cost_target': capital_cost_targ,
        'additional_investment': additional_investment,
        'additional_yearly_profit': additional_yearly_profit,
        'payback_years': payback_years,
        'fuel_per_flight_current_kg': curr_metrics['fuel_per_flight_kg'],
        'fuel_per_flight_target_kg': targ_metrics['fuel_per_flight_kg'],
        'co2_per_flight_current_kg': curr_metrics['co2_per_flight_kg'],
        'co2_per_flight_target_kg': targ_metrics['co2_per_flight_kg'],
        # New fields for UI
        'profit_source_current': curr_metrics['profit_source'],
        'profit_source_target': targ_metrics['profit_source'],
        'current_aircraft_id': cur_ac_id,
        'target_aircraft_id': tgt_ac_id,
        'origin_id': origin_id,
        'destination_id': dest_id
    }
