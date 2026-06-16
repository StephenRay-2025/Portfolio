import am4.utils.aircraft as ac
import am4.utils.airport as ap
import am4.utils.route as rt

print("=== Aircraft Search ===")
ares = ac.Aircraft.search("BAe146-300")
print(f"AircraftSearchResult: {ares}")
print(f"  ac: {getattr(ares, 'ac', 'NOT FOUND')}")
print(f"  parse_result: {getattr(ares, 'parse_result', 'NOT FOUND')}")
aircraft = getattr(ares, 'ac', None)
if aircraft:
    print(f"Aircraft object: {aircraft}")
    print(f"  id: {aircraft.id}")
    print(f"  name: {aircraft.name}")
    print(f"  cost: {aircraft.cost}")
    print(f"  fuel: {aircraft.fuel}")
    print(f"  range: {aircraft.range}")
    print(f"  co2: {aircraft.co2}")
else:
    print("No aircraft attribute")

print("\n=== Airport Search ===")
apres = ap.Airport.search("ATH")
print(f"AirportSearchResult: {apres}")
print(f"  ap: {getattr(apres, 'ap', 'NOT FOUND')}")
print(f"  parse_result: {getattr(apres, 'parse_result', 'NOT FOUND')}")
airport = getattr(apres, 'ap', None)
if airport:
    print(f"Airport object: {airport}")
    print(f"  id: {airport.id}")
    print(f"  name: {airport.name}")
    print(f"  iata: {airport.iata}")
    print(f"  icao: {airport.icao}")
    print(f"  lat: {airport.lat}")
    print(f"  lng: {airport.lng}")
else:
    print("No airport attribute")

print("\n=== Airport Search LHR ===")
lpres = ap.Airport.search("LHR")
lairport = getattr(lpres, 'ap', None) if lpres else None
if lairport:
    print(f"LHR Airport: {lairport.name} ({lairport.iata})")
else:
    print("LHR not found")

print("\n=== Route Calculation ===")
if aircraft and airport and lairport:
    origin = airport
    destination = lairport
    print(f"Origin: {origin.name} ({origin.iata})")
    print(f"Destination: {destination.name} ({destination.iata})")
    route = rt.Route(origin=origin, destination=destination)
    print(f"Route: {route}")
    print(f"Route attrs: {[a for a in dir(route) if not a.startswith('_')]}")
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

print("\n=== Suggest ===")
# suggest expects a ParseResult object
parse_obj = getattr(ares, 'parse_result', None)
if parse_obj is not None:
    sug = ac.Aircraft.suggest(parse_obj)
    print(f"Suggest results: {sug}")
    if isinstance(sug, list):
        for s in sug:
            print(f"  suggestion: {s}")
else:
    print("No parse_result for suggest")

print("\n=== Done ===")
