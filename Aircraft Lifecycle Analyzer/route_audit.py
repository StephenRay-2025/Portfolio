import pandas as pd
import sys
sys.path.append('/home/ubuntu/AM4user/analysis')
from datasets import dataset_service

# Load route data
route_path = '/home/ubuntu/AM4user/venv_spike/lib/python3.11/site-packages/am4/data/route.parquet'
df = pd.read_parquet(route_path)
print('1. route.parquet fields:')
print('   Columns:', list(df.columns))
print('   Description:')
print('     yd -> destination airport id (uint16)')
print('     jd -> origin airport id (uint16)')
print('     fd -> aircraft id (uint16)')
print('     d -> distance (float)')
print()

# Load aircraft and airports
aircraft = dataset_service.get_aircraft()
airports = dataset_service.get_airport()

print('2. Supported aircraft shortname (unique):')
shortnames = aircraft['shortname'].unique()
print('   Count:', len(shortnames))
print('   List:', ', '.join(sorted(shortnames)))
print()

print('3. Supported airport code (IATA):')
iatas = airports['iata'].unique()
print('   Count:', len(iatas))
print('   List:', ', '.join(sorted(iatas)))
print()

print('4. First 100 route samples (decoded):')
# Decode ids to names/codes
# Map aircraft id to shortname
ac_id_to_short = dict(zip(aircraft['id'], aircraft['shortname']))
# Map airport id to IATA
ap_id_to_iata = dict(zip(airports['id'], airports['iata']))

df_sample = df.head(100).copy()
df_sample['aircraft_short'] = df_sample['fd'].map(ac_id_to_short)
df_sample['origin_iata'] = df_sample['jd'].map(ap_id_to_iata)
df_sample['dest_iata'] = df_sample['yd'].map(ap_id_to_iata)
# Keep distance
df_sample['distance'] = df_sample['d']

# Show selected columns
cols_to_show = ['aircraft_short', 'origin_iata', 'dest_iata', 'distance']
print(df_sample[cols_to_show].to_string(index=False))
print()

# Pick a combination that exists: we can take the first row
first = df_sample.iloc[0]
ac_short = first['aircraft_short']
ori_iata = first['origin_iata']
dest_iata = first['dest_iata']
dist = first['distance']
print(f'Sample combination for testing:')
print(f'  Aircraft shortname: {ac_short}')
print(f'  Origin IATA: {ori_iata}')
print(f'  Destination IATA: {dest_iata}')
print(f'  Distance: {dist} km')
print()
# Verify that this combination exists in route dataset (it does by construction)
# Optionally, use dataset_service.find_routes to see if any routes exist
try:
    routes = dataset_service.find_routes(aircraft=ac_short, origin=ori_iata, destination=dest_iata)
    print(f'Found {len(routes)} route(s) for this combination via dataset_service.')
except Exception as e:
    print(f'Error querying dataset_service: {e}')