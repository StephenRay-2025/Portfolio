import am4.utils.aircraft as ac
import am4.utils.airport as ap
import am4.utils.route as rt

print("Testing aircraft module...")
print(dir(ac))
# see if there is a class Aircraft
if hasattr(ac, 'Aircraft'):
    print("Aircraft class found")
    Aircraft = ac.Aircraft
    print(Aircraft)
    # try to see if there are any class methods
    for attr in dir(Aircraft):
        if not attr.startswith('_'):
            print(f"  {attr}: {getattr(Aircraft, attr)}")
else:
    print("No Aircraft class")

print("\nTesting airport module...")
print(dir(ap))
if hasattr(ap, 'Airport'):
    print("Airport class found")
    Airport = ap.Airport
    print(Airport)
    for attr in dir(Airport):
        if not attr.startswith('_'):
            print(f"  {attr}: {getattr(Airport, attr)}")
else:
    print("No Airport class")

print("\nTesting route module...")
print(dir(rt))
# see if there are functions
for attr in dir(rt):
    if not attr.startswith('_'):
        print(f"  {attr}: {getattr(rt, attr)}")

# Try to instantiate Aircraft maybe with default?
print("\nTrying to create Aircraft instance...")
try:
    # maybe Aircraft requires parameters
    a = ac.Aircraft()
    print(f"Created: {a}")
except Exception as e:
    print(f"Error creating Aircraft: {e}")

# Try to call a function like get_aircrafts
if hasattr(ac, 'get_aircrafts'):
    try:
        lst = ac.get_aircrafts()
        print(f"Aircraft list: {lst}")
    except Exception as e:
        print(f"Error get_aircrafts: {e}")
if hasattr(ac, 'all'):
    try:
        lst = ac.all()
        print(f"Aircraft all: {lst}")
    except Exception as e:
        print(f"Error all: {e}")

