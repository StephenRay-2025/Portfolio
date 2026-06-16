#!/usr/bin/env python3
"""
Technical Spike for abc8747/am4
Demonstrates:
- Installation (import works)
- Aircraft query
- Airport query
- Route calculation
- Returned data structures
"""
import sys
import traceback

def main():
    print("=== Importing am4 ===")
    try:
        import am4
        import am4.utils.aircraft as ac
        import am4.utils.airport as ap
        import am4.utils.route as rt
        import am4.utils.db as db
        print("✓ Import successful")
    except Exception as e:
        print("✗ Import failed:", e)
        traceback.print_exc()
        sys.exit(1)

    print("\n=== Initializing DB (may download data) ===")
    try:
        db.init()
        print("✓ DB initialized")
    except Exception as e:
        print("⚠ DB init failed (will continue with possibly empty data):", e)
        # continue; maybe data missing

    print("\n--- Aircraft Search ---")
    try:
        # Search for a known model
        search_res = ac.Aircraft.search("A220-100")
        print(f"SearchResult object: {search_res}")
        # Attributes
        if hasattr(search_res, 'ac'):
            aircraft = search_res.ac
            print(f"Aircraft object: {aircraft}")
            print(f"  Type: {type(aircraft)}")
            # Show some properties
            for prop in ('id', 'name', 'cost', 'fuel', 'range', 'co2'):
                if hasattr(aircraft, prop):
                    val = getattr(aircraft, prop)
                    print(f"  {prop}: {val}")
            # Show dict representation
            if hasattr(aircraft, 'to_dict'):
                print(f"  as_dict: {aircraft.to_dict()}")
        else:
            print("  No 'ac' attribute (maybe data not loaded)")
            print(f"  Available attrs: {[a for a in dir(search_res) if not a.startswith('_')]}")
    except Exception as e:
        print("✗ Aircraft search error:", e)
        traceback.print_exc()

    print("\n--- Airport Search ---")
    try:
        search_res = ap.Airport.search("ATH")
        print(f"SearchResult object: {search_res}")
        if hasattr(search_res, 'ap'):
            airport = search_res.ap
            print(f"Airport object: {airport}")
            for prop in ('id', 'name', 'iata', 'icao', 'lat', 'lng'):
                if hasattr(airport, prop):
                    val = getattr(airport, prop)
                    print(f"  {prop}: {val}")
            if hasattr(airport, 'to_dict'):
                print(f"  as_dict: {airport.to_dict()}")
        else:
            print("  No 'ap' attribute")
            print(f"  Available attrs: {[a for a in dir(search_res) if not a.startswith('_')]}")
    except Exception as e:
        print("✗ Airport search error:", e)
        traceback.print_exc()

    print("\n--- Route Calculation ---")
    try:
        # Need valid aircraft and airport objects
        ac_obj = None
        ap1 = None
        ap2 = None
        # Try to get them again if possible
        try:
            ac_res = ac.Aircraft.search("A220-100")
            if hasattr(ac_res, 'ac'):
                ac_obj = ac_res.ac
        except: pass
        try:
            ap_res1 = ap.Airport.search("ATH")
            if hasattr(ap_res1, 'ap'):
                ap1 = ap_res1.ap
        except: pass
        try:
            ap_res2 = ap.Airport.search("LHR")
            if hasattr(ap_res2, 'ap'):
                ap2 = ap_res2.ap
        except: pass

        if ac_obj and ap1 and ap2:
            print(f"Aircraft: {ac_obj.name if hasattr(ac_obj,'name') else ac_obj}")
            print(f"Origin: {ap1.name if hasattr(ap1,'name') else ap1} ({ap1.iata if hasattr(ap1,'iata') else '??'})")
            print(f"Destination: {ap2.name if hasattr(ap2,'name') else ap2} ({ap2.iata if hasattr(ap2,'iata') else '??'})")
            # Route
            route = rt.Route(origin=ap1, destination=ap2)
            print(f"Route object: {route}")
            for prop in ('distance', 'great_circle_distance', 'duration'):
                if hasattr(route, prop):
                    val = getattr(route, prop)
                    print(f"  {prop}: {val}")
            # AircraftRoute
            air_route = rt.AircraftRoute(aircraft=ac_obj, origin=ap1, destination=ap2)
            print(f"AircraftRoute object: {air_route}")
            for prop in ('fuel', 'cost', 'profit', 'co2'):
                if hasattr(air_route, prop):
                    val = getattr(air_route, prop)
                    print(f"  {prop}: {val}")
            if hasattr(air_route, 'to_dict'):
                print(f"  as_dict: {air_route.to_dict()}")
        else:
            print("⚠ Could not obtain valid aircraft/airport objects (data may be missing).")
            # Still show that the classes exist and can be instantiated with dummy data? Not possible without valid objects.
            print("  Available route classes:", [c for c in dir(rt) if not c.startswith('_') and isinstance(getattr(rt, c), type)])
    except Exception as e:
        print("✗ Route calculation error:", e)
        traceback.print_exc()

    print("\n=== Summary of Data Structures ===")
    print("""
    Aircraft SearchResult:
      - .ac : am4.utils.aircraft.Aircraft instance (or Aircraft.INVALID if data missing)
      - .parse_result : internal ParseResult (used for suggest)

    Aircraft instance properties (examples):
      id, name, cost, fuel, range, co2, speed, length, wingspan, etc.
      .to_dict() -> dict

    Airport SearchResult:
      - .ap : am4.utils.airport.Airport instance (or Airport.INVALID)
      - .parse_result : internal ParseResult

    Airport instance properties:
      id, name, iata, icao, lat, lng, continent, country, hub_cost, market, etc.
      .to_dict() -> dict

    Route (origin: Airport, destination: Airport):
      distance, great_circle_distance, duration (hours)
      (potentially more depending on implementation)

    AircraftRoute (aircraft: Aircraft, origin: Airport, destination: Airport):
      fuel (kg), cost (USD), profit (USD), co2 (kg)
      .to_dict() -> dict

    All above objects provide a .to_dict() method for easy serialization.
    """)
    print("=== Spike completed ===")

if __name__ == '__main__':
    main()
