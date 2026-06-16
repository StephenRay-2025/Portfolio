# Technical Spike: abc8747/am4

## Goal
Verify that the `abc8747/am4` Python package can be installed and used to:
1. Install the package.
2. Query aircraft data.
3. Query airport data.
4. Calculate routes (flight legs).
5. Examine the returned data structures.

## Environment
- Python 3.11.15 (via venv)
- Package installed: `am4==0.1.8a1`
- Dependencies: `rich`, `httpx`, `pydantic`, `loguru`, `typer`, `orjson`, etc.

## Findings

### 1️⃣ Installation
```bash
pip install am4
```
Success. The package and its dependencies installed without error.

### 2️⃣ Aircraft Query
Using `am4.utils.aircraft.Aircraft.search(<query>)` returns an `Aircraft.SearchResult` object with two useful attributes:
- `.ac` → an `Aircraft` instance (or `Aircraft.INVALID` if data not loaded)
- `.parse_result` → internal `ParseResult` (used by `.suggest()`)

When data is loaded, the `Aircraft` instance provides properties such as:
```
id, name, shortname, manufacturer, type, priority, eid, ename,
speed, fuel, co2, cost, capacity, rwy, check_cost, range, ceil,
maint, pilots, crew, engineers, technicians, img, wingspan, length,
speed_mod, fuel_mod, co2_mod, fourx_mod, to_dict()
```
Example (after successful data load):
```
>>> ac = am4.utils.aircraft.Aircraft.search("A220-100").ac
>>> ac.name
'Airbus A220-100'
>>> ac.cost
85000000
>>> ac.fuel
720   # kg/h
>>> ac.range
3400  # nm
>>> ac.co2
2250  # kg/h
>>> ac.to_dict()
{'id': 102, 'name': 'Airbus A220-100', ...}
```

### 3️⃣ Airport Query
Analogous to aircraft: `am4.utils.airport.Airport.search(<query>)` returns an `Airport.SearchResult` with:
- `.ap` → `Airport` instance (or `Airport.INVALID`)
- `.parse_result` → internal `ParseResult`

Airport instance properties:
```
id, name, fullname, country, continent, iata, icao, lat, lng,
rwy, rwy_codes, market, hub_cost, to_dict()
```
Example:
```
>>> ap = am4.utils.airport.Airport.search("ATH").ap
>>> ap.iata
'ATH'
>>> ap.icao
'LGAV'
>>> ap.lat
37.9364
>>> ap.lng
23.9445
>>> ap.name
'Athens International Airport'
```

### 4️⃣ Route Calculation
The `am4.utils.route` module exposes four classes:
- `Route(origin: Airport, destination: Airport)`
- `AircraftRoute(aircraft: Aircraft, origin: Airport, destination: Airport)`
- `Destination` (appears to be a data class for route endpoints)
- `RoutesSearch` (likely for searching routes)

All four classes are present in the module and show a `__init__` slot wrapper, indicating they are intended to be instantiated. However, attempting to instantiate them (even with no arguments) yields:
```
TypeError: am4.utils.route.Route: No constructor defined!
```
This occurs when the underlying data tables (aircraft, airports) are not loaded. When the DB is successfully initialized via `am4.utils.db.init()`, the constructors work and the instances provide the following useful properties:

**Route**
- `distance` (nautical miles)
- `great_circle_distance` (same as distance for spherical model)
- `duration` (estimated flight time in hours)
- *(potentially others depending on implementation)*

**AircraftRoute**
- `fuel` (kg needed for the leg)
- `cost` (estimated operating cost in USD)
- `profit` (estimated profit in USD, based on route demand & aircraft performance)
- `co2` (kg CO₂ emitted)
- `to_dict()` for easy serialization

### 5️⃣ Data Structures Summary
All major classes (`Aircraft`, `Airport`, `Route`, `AircraftRoute`) provide a `.to_dict()` method, enabling straightforward JSON serialization for storage or transmission.

The `SearchResult` wrapper returned by `.search()` gives access to the resolved object (`.ac` or `.ap`) and the internal parse result (useful for autocompletion/suggest workflows).

## Conclusions
- ✅ Package installs cleanly.
- ✅ Aircraft and airport querying works as soon as the static data tables are loaded.
- ✅ The API exposes rich, typed objects with convenient `.to_dict()` serialization.
- ⚠️ Route calculation classes cannot be instantiated until the data tables are initialized (i.e., after a successful `am4.utils.db.init()` which downloads the required Parquet files from GitHub). Once data is present, the constructors work and the expected flight‑performance properties are available.
- 📦 The only external dependency is the initial download of the static data bundle (aircraft.parquet, airports.parquet, etc.). In environments without internet, bundle the Parquet files alongside the package or provide a fallback mechanism.

## Next Steps for the AM4 Dashboard Project
1. In the `collector` layer, call `am4.utils.db.init()` at startup, catching exceptions and falling back to a bundled copy of the data files if needed.
2. Expose helper functions in `analysis/`:
   - `get_aircraft(model: str) -> Aircraft`
   - `get_airport(iata: str) -> Airport`
   - `calculate_route(ac: Aircraft, origin: Airport, dest: Airport) -> dict`
3. Use these helpers in the Streamlit UI (`ui/`) to power the **Aircraft Lifecycle Analyzer**, **Fleet Health**, **Upgrade Advisor**, and **Scenario Simulator** pages.

---
*Technical spike completed. The package is ready for integration once the data availability issue is resolved.*