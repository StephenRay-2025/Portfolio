import am4.utils.aircraft as ac
import am4.utils.airport as ap
import am4.utils.route as rt

print("=== Aircraft Search ===")
# Search for BAe146
results = ac.Aircraft.search("BAe146-300")
print(f"Search results for 'BAe146-300': {results}")
if results:
    # Assuming results is a list of Aircraft.SearchResult objects
    for r in results[:3]:
        print(f"  Result: {r}")
        # maybe get the actual aircraft via r.aircraft or r.get()
        if hasattr(r, 'aircraft'):
            aircraft = r.aircraft
            print(f"    Aircraft: {aircraft}")
            print(f"      id: {aircraft.id}")
            print(f"      name: {aircraft.name}")
            print(f"      cost: {aircraft.cost}")
            print(f"      fuel: {aircraft.fuel}")
            print(f"      range: {aircraft.range}")
            print(f"      co2: {aircraft.co2}")
        elif hasattr(r, 'to_dict'):
            print(f"    Dict: {r.to_dict()}")

print("\n=== Airport Search ===")
# Search for airport with IATA "ATH"
results_ap = ap.Airport.search("ATH")
print(f"Search results for 'ATH': {results_ap}")
if results_ap:
    for r in results_ap[:3]:
        print(f"  Result: {r}")
        if hasattr(r, 'airport'):
            airport = r.airport
            print(f"    Airport: {airport}")
            print(f"      id: {airport.id}")
            print(f"      name: {airport.name}")
            print(f"      iata: {airport.iata}")
            print(f"      icao: {airport.icao}")
            print(f"      lat: {airport.lat}")
            print(f"      lng: {airport.lng}")
        elif hasattr(r, 'to_dict'):
            print(f"    Dict: {r.to_dict()}")

print("\n=== Route Calculation ===")
# Try to create a Route between two airports
# First get two airport objects
ath_result = ap.Airport.search("ATH")
lhr_result = ap.Airport.search("LHR")
if ath_result and lhr_result:
    ath_airport = ath_result[0].airport if hasattr(ath_result[0], 'airport') else ath_result[0]
    lhr_airport = lhr_result[0].airport if hasattr(lhr_result[0], 'airport') else lhr_result[0]
    print(f"Origin: {ath_airport.name} ({ath_airport.iata})")
    print(f"Destination: {lhr_airport.name} ({lhr_airport.iata})")
    # Create a Route object
    route = rt.Route(origin=ath_airport, destination=lhr_airport)
    print(f"Route object: {route}")
    # See what properties/methods route has
    print(f"Route attributes: {[a for a in dir(route) if not a.startswith('_')]}")
    # Try to get distance
    if hasattr(route, 'distance'):
        print(f"Distance: {route.distance}")
    if hasattr(route, 'great_circle_distance'):
        print(f"Great circle distance: {route.great_circle_distance}")
    if hasattr(route, 'duration'):
        print(f"Duration: {route.duration}")
    # Maybe there is a method to compute fuel cost etc.
    # Also try AircraftRoute for a specific aircraft
    if ac_result := ac.Aircraft.search("A220-100"):
        aircraft_obj = ac_result[0].aircraft if hasattr(ac_result[0], 'aircraft') else ac_result[0]
        print(f"\nUsing aircraft: {aircraft_obj.name}")
        air_route = rt.AircraftRoute(aircraft=aircraft_obj, origin=ath_airport, destination=lhr_airport)
        print(f"AircraftRoute: {air_route}")
        if hasattr(air_route, 'fuel'):
            print(f"Fuel needed: {air_route.fuel}")
        if hasattr(air_route, 'cost'):
            print(f"Cost: {air_route.cost}")
        if hasattr(air_route, 'profit'):
            print(f"Profit estimate: {air_route.profit}")
else:
    print("Could not find airports for ATH and LHR")

print("\n=== Testing Route Search ===")
# Maybe there is a RoutesSearch class for searching routes?
if hasattr(rt, 'RoutesSearch'):
    search = rt.RoutesSearch()
    print(f"RoutesSearch: {search}")
    # maybe search by origin/destination
    pass

print("\n=== Done ===")
