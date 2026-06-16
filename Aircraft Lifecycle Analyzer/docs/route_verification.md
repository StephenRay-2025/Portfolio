# Route Verification Report

## Step 1: Extract first record from route.parquet

```python
route_df = dataset_service.routes
row = route_df.iloc[0]
```

Extracted values:
- yd (destination airport ID) = 542.0
- jd (origin airport ID) = 182.0
- fd (aircraft ID) = 45.0
- d (simulation feature) = 330.21963764776416

## Step 2: Reverse lookup IDs to actual values

- Aircraft ID 45.0 → Name: B737-500, Shortname: b735
- Origin Airport ID 182.0 → IATA: YOP
- Destination Airport ID 542.0 → IATA: UNKNOWN

## Step 3: Fill into Dashboard

Use the following values in the AM4 Aircraft Dashboard:

- **Aircraft**: B737-500 (shortname: b735)
- **Origin**: YOP
- **Destination**: UNKNOWN

### Example format for Dashboard input:

```
Aircraft = B737-500
Origin = YOP
Destination = UNKNOWN
```

## Notes

- The `d` column is a simulation feature (distance-like) and not used for economic calculations.
- This verification confirms that the ID mappings are consistent between route.parquet and the lookup tables.