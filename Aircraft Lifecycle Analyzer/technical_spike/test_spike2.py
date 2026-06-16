import am4.utils.aircraft as ac
import am4.utils.airport as ap
import am4.utils.route as rt

def inspect(obj, name):
    print(f"\n{name} object type: {type(obj)}")
    print(f"  dir: {[a for a in dir(obj) if not a.startswith('_')]}")
    # try to see if it's iterable
    try:
        iter(obj)
        print("  is iterable")
    except:
        pass

print("=== Aircraft Search ===")
results = ac.Aircraft.search("BAe146-300")
inspect(results, "SearchResult")
# If it's a single result, get aircraft
if hasattr(results, 'aircraft'):
    aircraft = results.aircraft
    print(f"Aircraft: {aircraft}")
    print(f"  id: {aircraft.id}")
    print(f"  name: {aircraft.name}")
    print(f"  cost: {aircraft.cost}")
    print(f"  fuel: {aircraft.fuel}")
    print(f"  range: {aircraft.range}")
    print(f"  co2: {aircraft.co2}")
elif hasattr(results, 'to_dict'):
    print(f"As dict: {results.to_dict()}")
else:
    print("No known attribute to get aircraft")

print("\n=== Airport Search ===")
ap_result = ap.Airport.search("ATH")
inspect(ap_result, "Airport SearchResult")
if hasattr(ap_result, 'airport'):
    airport = ap_result.airport
    print(f"Airport: {airport}")
    print(f"  id: {airport.id}")
    print(f"  name: {airport.name}")
    print(f"  iata: {airport.iata}")
    print(f"  icao: {airport.icao}")
    print(f"  lat: {airport.lat}")
    print(f"  lng: {airport.lng}")
elif hasattr(ap_result, 'to_dict'):
    print(f"As dict: {ap_result.to_dict()}")

print("\n=== Get second airport LHR ===")
lhr_result = ap.Airport.search("LHR")
if hasattr(lhr_result, 'airport'):
    lhr_airport = lhr_result.airport
    print(f"LHR Airport: {lhr_airport.name} ({lhr_airport.iata})")
else:
    print("Could not get LHR")

print("\n=== Route Calculation ===")
if 'aircraft' in locals() and 'airport' in locals() and 'lhr_airport' in locals():
    origin = airport
    destination = lhr_airport
    print(f"Origin: {origin.name} ({origin.iata})")
    print(f"Destination: {destination.name} ({destination.iata})")
    route = rt.Route(origin=origin, destination=destination)
    print(f"Route: {route}")
    print(f"Route attrs: {[a for a in dir(route) if not a.startswith('_')]}")
    # try to get distance
    if hasattr(route, 'distance'):
        print(f"Distance: {route.distance}")
    if hasattr(route, 'great_circle_distance'):
        print(f"Great circle distance: {route.great_circle_distance}")
    if hasattr(route, 'duration'):
        print(f"Duration: {route.duration}")
    # AircraftRoute
    air_route = rt.AircraftRoute(aircraft=aircraft, origin=origin, destination=destination)
    print(f"AircraftRoute: {air_route}")
    print(f"AircraftRoute attrs: {[a for a in dir(air_route) if not a.startswith('_')]}")
    if hasattr(air_route, 'fuel'):
        print(f"Fuel needed: {air_route.fuel}")
    if hasattr(air_route, 'cost'):
        print(f"Cost: {air_route.cost}")
    if hasattr(air_route, 'profit'):
        print(f"Profit: {air_route.profit}")
    if hasattr(air_route, 'co2'):
        print(f"CO2: {air_route.co2}")
else:
    print("Missing data for route calculation")

print("\n=== Testing suggest maybe ===")
# Suggest method
sug = ac.Aircraft.suggest("A220")
print(f"Aircraft suggest 'A220': {sug}")
if hasattr(sug, '__iter__'):
    try:
        for s in sug:
            print(f"  suggestion: {s}")
    except:
        pass
else:
    print(f"  suggest result: {sug}")

print("\n=== Done ===")
