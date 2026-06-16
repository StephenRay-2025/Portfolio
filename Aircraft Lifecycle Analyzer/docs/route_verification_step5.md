# Route Verification Report (Step-by-step)

## Step 1: Extract the 5th record (index 4) from route.parquet

```python
route_df = dataset_service.routes
row5 = route_df.iloc[4]  # 5th record
```

Extracted values:
- yd (destination airport ID) = 389.0
- jd (origin airport ID) = 132.0
- fd (aircraft ID) = 76.0
- d (simulation feature) = 1849.1149956899344

## Step 2: Reverse lookup IDs to actual values

- Aircraft ID 76.0 → Name: B777-300LR, Shortname: b773lr
- Origin Airport ID 132.0 → IATA: YIK
- Destination Airport ID 389.0 → IATA: OUA

## Step 3: Query for Aircraft = A220-100, Origin = PEK, Destination = SIN in route.parquet

Mapping inputs to internal IDs:
- Aircraft 'A220-100' → internal ID: 322
- Origin 'PEK' → internal ID: 3890
- Destination 'SIN' → internal ID: 3731

Search condition: yd == destination ID AND jd == origin ID AND fd == aircraft ID

No matching record found for the exact combination (A220-100, PEK, SIN) in route.parquet.

## Notes

- The `d` column is a simulation feature (distance‑like) and not used for economic calculations.
- If no match is found, it may indicate that the specific aircraft‑origin‑destination combination is not present in the simulated dataset.
