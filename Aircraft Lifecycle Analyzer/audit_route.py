import pandas as pd
import os
path = '/home/ubuntu/AM4user/venv_spike/lib/python3.11/site-packages/am4/data/route.parquet'
print('Reading parquet...')
df = pd.read_parquet(path)
print('Shape:', df.shape)
print('Columns:', df.columns.tolist())
print('\\nFirst 5 rows:')
print(df.head())
print('\\nAircraft shortname column? Let\\'s see unique values in aircraft column if exists.')
# Check for aircraft column
aircraft_cols = [c for c in df.columns if 'aircraft' in c.lower() or 'ac' in c.lower()]
print('Possible aircraft columns:', aircraft_cols)
# Check for origin/destination
origin_cols = [c for c in df.columns if 'origin' in c.lower() or 'ori' in c.lower()]
dest_cols = [c for c in df.columns if 'destination' in c.lower() or 'dest' in c.lower() or 'fd' in c.lower()]
print('Possible origin columns:', origin_cols)
print('Possible destination columns:', dest_cols)
# If not found, maybe columns are coded as yd, jd, fd, d as earlier debug showed.
# Let's see unique values in each column
for col in df.columns:
    if df[col].dtype == 'object':
        uniq = df[col].dropna().unique()
        print(f'{col}: {len(uniq)} unique values, sample: {uniq[:10]}')
    else:
        print(f'{col}: numeric, min={df[col].min()}, max={df[col].max()}')
# Now try to identify aircraft shortname, origin, destination based on earlier debug output
# Earlier debug showed columns: yd, jd, fd, d
# Let's assume fd is aircraft? jd? yd? Not sure.
# We'll load the datasets service to map shortnames to names maybe.
# But for now, just output unique values of each column.
print('\\n=== Unique values per column (first 20) ===')
for col in df.columns:
    if df[col].dtype == 'object':
        uniq = df[col].dropna().unique()[:20]
        print(f'{col}: {list(uniq)}')
    else:
        # numeric, show min/max and maybe unique count
        uniq_cnt = df[col].nunique()
        print(f'{col}: numeric, unique={uniq_cnt}, min={df[col].min()}, max={df[col].max()}')