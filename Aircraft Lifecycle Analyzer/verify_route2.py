import sys
sys.path.insert(0, '.')
from analysis.datasets import dataset_service
import pandas as pd

# Helper to get internal IDs
def get_aircraft_id_by_name(name):
    ac = dataset_service.get_aircraft_by_name(name)
    if ac is None:
        raise ValueError(f"Aircraft '{name}' not found")
    return int(ac['id'])

def get_airport_id_by_iata(iata):
    ap = dataset_service.get_airport_by_code(iata.upper())
    if ap is None:
        raise ValueError(f"Airport IATA '{iata}' not found")
    return int(ap['id'])

def get_aircraft_shortname_by_id(ac_id):
    ac_df = dataset_service.aircraft
    row = ac_df[ac_df['id'] == ac_id]
    if row.empty:
        return None
    return row.iloc[0]['shortname']

def get_aircraft_name_by_id(ac_id):
    ac_df = dataset_service.aircraft
    row = ac_df[ac_df['id'] == ac_id]
    if row.empty:
        return None
    return row.iloc[0]['name']

def get_airport_iata_by_id(ap_id):
    ap_df = dataset_service.airports
    row = ap_df[ap_df['id'] == ap_id]
    if row.empty:
        return None
    return row.iloc[0]['iata']

# Step 1: Take 5th record (index 4) from route.parquet
route_df = dataset_service.routes
if len(route_df) < 5:
    print("route.parquet has less than 5 records")
    sys.exit(1)

row5 = route_df.iloc[4]  # zero-index
yd = row5['yd']
jd = row5['jd']
fd = row5['fd']
d_val = row5['d']
print(f"Step 1: 5th record (index 4): yd={yd}, jd={jd}, fd={fd}, d={d_val}")

# Step 2: Reverse lookup
# Aircraft
aircraft_name = get_aircraft_name_by_id(fd)
aircraft_short = get_aircraft_shortname_by_id(fd)
# Origin airport (jd)
origin_iata = get_airport_iata_by_id(jd)
# Destination airport (yd)
dest_iata = get_airport_iata_by_id(yd)

print(f"Step 2: Reverse lookup:")
print(f"  Aircraft ID {fd} -> Name: {aircraft_name}, Shortname: {aircraft_short}")
print(f"  Origin Airport ID {jd} -> IATA: {origin_iata}")
print(f"  Destination Airport ID {yd} -> IATA: {dest_iata}")

# Step 3: Query for Aircraft = A220-100, Origin = PEK, Destination = SIN
try:
    ac_id_A220 = get_aircraft_id_by_name('A220-100')
    origin_id_PEK = get_airport_id_by_iata('PEK')
    dest_id_SIN = get_airport_id_by_iata('SIN')
except Exception as e:
    print(f"Error in mapping inputs: {e}")
    sys.exit(1)

print(f"\nStep 3: Query parameters:")
print(f"  A220-100 -> internal aircraft ID: {ac_id_A220}")
print(f"  PEK -> origin airport ID: {origin_id_PEK}")
print(f"  SIN -> destination airport ID: {dest_id_SIN}")

# Find matching rows in route.parquet where yd == dest_id_SIN, jd == origin_id_PEK, fd == ac_id_A220
mask = (route_df['yd'] == dest_id_SIN) & (route_df['jd'] == origin_id_PEK) & (route_df['fd'] == ac_id_A220)
matching = route_df[mask]
print(f"\nNumber of matching records: {len(matching)}")
if len(matching) > 0:
    # Show first match
    first = matching.iloc[0]
    print(f"First matching record:")
    print(f"  yd={first['yd']}, jd={first['jd']}, fd={first['fd']}, d={first['d']}")
else:
    print("No exact match found.")
    # Optionally show close matches? Not needed.

# Prepare report
report_lines = []
report_lines.append("# Route Verification Report (Step-by-step)")
report_lines.append("")
report_lines.append("## Step 1: Extract the 5th record (index 4) from route.parquet")
report_lines.append("")
report_lines.append("```python")
report_lines.append("route_df = dataset_service.routes")
report_lines.append("row5 = route_df.iloc[4]  # 5th record")
report_lines.append("```")
report_lines.append("")
report_lines.append("Extracted values:")
report_lines.append(f"- yd (destination airport ID) = {yd}")
report_lines.append(f"- jd (origin airport ID) = {jd}")
report_lines.append(f"- fd (aircraft ID) = {fd}")
report_lines.append(f"- d (simulation feature) = {d_val}")
report_lines.append("")
report_lines.append("## Step 2: Reverse lookup IDs to actual values")
report_lines.append("")
report_lines.append(f"- Aircraft ID {fd} → Name: {aircraft_name if aircraft_name else 'NOT FOUND'}, Shortname: {aircraft_short if aircraft_short else 'NOT FOUND'}")
report_lines.append(f"- Origin Airport ID {jd} → IATA: {origin_iata if origin_iata else 'NOT FOUND'}")
report_lines.append(f"- Destination Airport ID {yd} → IATA: {dest_iata if dest_iata else 'NOT FOUND'}")
report_lines.append("")
report_lines.append("## Step 3: Query for Aircraft = A220-100, Origin = PEK, Destination = SIN in route.parquet")
report_lines.append("")
report_lines.append("Mapping inputs to internal IDs:")
report_lines.append(f"- Aircraft 'A220-100' → internal ID: {ac_id_A220}")
report_lines.append(f"- Origin 'PEK' → internal ID: {origin_id_PEK}")
report_lines.append(f"- Destination 'SIN' → internal ID: {dest_id_SIN}")
report_lines.append("")
report_lines.append("Search condition: yd == destination ID AND jd == origin ID AND fd == aircraft ID")
report_lines.append("")
if len(matching) > 0:
    first = matching.iloc[0]
    report_lines.append("Matching record found:")
    report_lines.append(f"- yd (destination ID) = {first['yd']}")
    report_lines.append(f"- jd (origin ID) = {first['jd']}")
    report_lines.append(f"- fd (aircraft ID) = {first['fd']}")
    report_lines.append(f"- d (simulation feature) = {first['d']}")
else:
    report_lines.append("No matching record found for the exact combination (A220-100, PEK, SIN) in route.parquet.")
report_lines.append("")
report_lines.append("## Notes")
report_lines.append("")
report_lines.append("- The `d` column is a simulation feature (distance‑like) and not used for economic calculations.")
report_lines.append("- If no match is found, it may indicate that the specific aircraft‑origin‑destination combination is not present in the simulated dataset.")
report_lines.append("")
report_content = "\n".join(report_lines)

output_path = "/home/ubuntu/AM4user/docs/route_verification_step5.md"
with open(output_path, "w") as f:
    f.write(report_content)
print(f"\nReport written to {output_path}")