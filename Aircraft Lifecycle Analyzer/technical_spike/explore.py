import am4.utils.db
import am4.utils.aircraft
import am4.utils.airport
import am4.utils.route

print("Initializing DB...")
am4.utils.db.init()
print("DB initialized.")

print("\nAircraft utils:")
print(dir(am4.utils.aircraft))
print("\nAirport utils:")
print(dir(am4.utils.airport))
print("\nRoute utils:")
print(dir(am4.utils.route))

# Try to get aircraft list
if hasattr(am4.utils.aircraft, 'get_all'):
    try:
        aircrafts = am4.utils.aircraft.get_all()
        print(f"\nAircraft count via get_all: {len(aircrafts)}")
        print(aircrafts[:2])
    except Exception as e:
        print(f"Error in get_all: {e}")
elif hasattr(am4.utils.aircraft, 'all'):
    try:
        aircrafts = am4.utils.aircraft.all()
        print(f"\nAircraft count via all: {len(aircrafts)}")
        print(aircrafts[:2])
    except Exception as e:
        print(f"Error in all: {e}")
else:
    # try Aircraft class
    try:
        # maybe Aircraft.select()
        from am4.utils.aircraft import Aircraft
        print(f"Aircraft class: {Aircraft}")
        # check if there is a .select() method
        if hasattr(Aircraft, 'select'):
            qs = Aircraft.select()
            print(f"Select query: {qs}")
            # maybe execute
            aircrafts = list(qs)
            print(f"Aircraft count via select: {len(aircrafts)}")
            for a in aircrafts[:2]:
                print(a)
        else:
            print("No select method")
    except Exception as e:
        print(f"Error accessing Aircraft: {e}")

# Similar for airport
if hasattr(am4.utils.airport, 'get_all'):
    try:
        airports = am4.utils.airport.get_all()
        print(f"\nAirport count via get_all: {len(airports)}")
        print(airports[:2])
    except Exception as e:
        print(f"Error in airport get_all: {e}")
elif hasattr(am4.utils.airport, 'all'):
    try:
        airports = am4.utils.airport.all()
        print(f"\nAirport count via all: {len(airports)}")
        print(airports[:2])
    except Exception as e:
        print(f"Error in airport all: {e}")
else:
    try:
        from am4.utils.airport import Airport
        if hasattr(Airport, 'select'):
            qs = Airport.select()
            airports = list(qs)
            print(f"\nAirport count via select: {len(airports)}")
            for a in airports[:2]:
                print(a)
        else:
            print("Airport no select")
    except Exception as e:
        print(f"Error accessing Airport: {e}")

# Try route calculation
print("\n--- Route calculation test ---")
if hasattr(am4.utils.route, 'calculate'):
    try:
        # need origin and destination airport IDs or objects
        # we need to get some airports first
        from am4.utils.airport import Airport
        airports = list(Airport.select().limit(2))
        if len(airports) >= 2:
            origin = airports[0]
            dest = airports[1]
            print(f"Origin: {origin}, Destination: {dest}")
            # maybe calculate route distance etc.
            if hasattr(am4.utils.route, 'distance'):
                dist = am4.utils.route.distance(origin, dest)
                print(f"Distance: {dist}")
            else:
                print("No distance function")
        else:
            print("Not enough airports to test route")
    except Exception as e:
        print(f"Error in route calculation: {e}")
else:
    print("No route.calculate function")

