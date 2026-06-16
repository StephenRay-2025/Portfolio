#!/usr/bin/env python3
# Test script for am4 package: AircraftRoute and RoutesSearch
import sys
import traceback
import faulthandler
faulthandler.enable()  # Enable to get traceback on segfault

def main():
    print("Testing am4 package...")
    try:
        import am4
        print(f"am4 imported successfully")
        # Try to get version if available
        if hasattr(am4, '__version__'):
            print(f"am4 version: {am4.__version__}")
        else:
            print("am4 has no __version__ attribute")
    except Exception as e:
        print(f"Failed to import am4: {e}")
        traceback.print_exc()
        return

    try:
        import am4.utils.db as db
        print("Initializing database...")
        db.init()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        traceback.print_exc()
        return

    try:
        from am4.utils.route import AircraftRoute, RoutesSearch
        print("Imported AircraftRoute and RoutesSearch")
    except Exception as e:
        print(f"Failed to import route utilities: {e}")
        traceback.print_exc()
        return

    # Test AircraftRoute: A220-100, PEK -> SIN
    try:
        print("\nTesting AircraftRoute for A220-100 PEK->SIN")
        # First get aircraft and airport objects
        from am4.utils.aircraft import Aircraft
        from am4.utils.airport import Airport
        # Search for aircraft
        ac_result = Aircraft.search('A220-100')
        if not ac_result:
            print("Aircraft not found")
            return
        aircraft = ac_result.ac  # Assuming SearchResult has .ac attribute
        print(f"Aircraft: {aircraft}")
        # Search for airports
        pek_result = Airport.search('PEK')
        sin_result = Airport.search('SIN')
        if not pek_result or not sin_result:
            print("Airport not found")
            return
        pek_ap = pek_result.ac
        sin_ap = sin_result.ac
        print(f"Origin: {pek_ap}, Destination: {sin_ap}")
        # Create AircraftRoute
        route = AircraftRoute(aircraft=aircraft, origin=pek_ap, destination=sin_ap)
        print(f"AircraftRoute created: {route}")
        # Test attributes
        print(f"Profit: {getattr(route, 'profit', 'N/A')}")
        print(f"Cost: {getattr(route, 'cost', 'N/A')}")
        print(f"Fuel: {getattr(route, 'fuel', 'N/A')}")
        print(f"CO2: {getattr(route, 'co2', 'N/A')}")
        print(f"Distance: {getattr(route, 'distance', 'N/A')}")
    except Exception as e:
        print(f"Error testing AircraftRoute: {e}")
        traceback.print_exc()

    # Test RoutesSearch: from PEK to all destinations
    try:
        print("\nTesting RoutesSearch from PEK")
        from am4.utils.airport import Airport
        pek_result = Airport.search('PEK')
        if not pek_result:
            print("PEK airport not found")
            return
        pek_ap = pek_result.ac
        search = RoutesSearch(origin=pek_ap)
        print(f"RoutesSearch created: {search}")
        # Get results? Might need to call .search() or similar
        # Let's see if there's a method to get destinations
        if hasattr(search, 'destinations'):
            dests = search.destinations
            print(f"Number of destinations: {len(dests)}")
            for i, d in enumerate(dests[:5]):  # show first 5
                print(f"  {i}: {d}")
        else:
            print("Search object does not have 'destinations' attribute; checking dir:")
            print([attr for attr in dir(search) if not attr.startswith('_')])
    except Exception as e:
        print(f"Error testing RoutesSearch: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()