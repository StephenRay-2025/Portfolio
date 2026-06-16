#!/usr/bin/env python3
"""
Decode route.parquet schema for AM4user project.

Goal:
1. Find meaning of yd/jd/fd columns.
2. Determine if d is profit/demand/score etc.
3. Provide basic statistics and histogram of d.
"""

import pandas as pd
import numpy as np
import os

def main():
    # Path to route.parquet (as seen in environment)
    parquet_path = '/home/ubuntu/AM4user/venv_spike/lib/python3.11/site-packages/am4/data/route.parquet'
    if not os.path.exists(parquet_path):
        # Fallback: maybe relative
        parquet_path = 'venv_spike/lib/python3.11/site-packages/am4/data/route.parquet'
    print(f"Loading route data from: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    
    print("\n=== 1. route.parquet shape and columns ===")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    print("\n=== 2. Descriptive statistics (df.describe()) ===")
    print(df.describe())
    
    print("\n=== 3. Correlation matrix (df.corr()) ===")
    print(df.corr())
    
    print("\n=== 4. First 100 rows (df.head(100)) ===")
    print(df.head(100))
    
    print("\n=== 5. Column-wise unique values and samples ===")
    for col in df.columns:
        if df[col].dtype == 'object':
            uniq = df[col].dropna().unique()
            print(f"{col}: {len(uniq)} unique values (object). Sample: {uniq[:5] if len(uniq) > 0 else []}")
        else:
            uniq = df[col].dropna().unique()
            print(f"{col}: {len(uniq)} unique values, min={df[col].min():.4f}, max={df[col].max():.4f}, mean={df[col].mean():.4f}")
            # Show a few sample values
            sample = df[col].dropna().sample(min(5, len(uniq)), random_state=42)
            print(f"  Sample values: {sample.tolist()}")
    
    print("\n=== 6. Histogram of d (profit/score/demand) ===")
    # Determine if d looks like a continuous score, profit, etc.
    d_vals = df['d'].dropna()
    # Compute histogram with 20 bins
    hist, bin_edges = np.histogram(d_vals, bins=20)
    print("Histogram counts (20 bins):")
    for i in range(len(hist)):
        print(f"  [{bin_edges[i]:.2f}, {bin_edges[i+1]:.2f}): {hist[i]}")
    # Basic shape metrics
    skew = d_vals.skew()
    kurt = d_vals.kurtosis()
    print(f"\nSkewness: {skew:.4f}")
    print(f"Kurtosis: {kurt:.4f}")
    # If skewness near 0 and kurtosis near 3 -> roughly normal (score-like)
    # If highly positive skew -> maybe revenue/profit (many low values, few high)
    # If discrete integer-like -> maybe category
    # Check if values are integers
    if np.all(np.equal(np.mod(d_vals, 1), 0)):
        print("Values are all integers -> likely categorical or ID.")
    else:
        print("Values are continuous (non-integer).")
    
    print("\n=== 7. Interpretation guess ===")
    print("Based on column names and earlier debugging:")
    print("  yd -> destination airport ID (uint16)")
    print("  jd -> origin airport ID (uint16)")
    print("  fd -> aircraft ID (uint16)")
    print("  d -> distance? Actually earlier we saw d is float and used as profit per flight.")
    print("  In lifecycle.py, get_route_profit returns float(df.iloc[0]['d']) and is treated as profit.")
    print("  However the column might represent distance (km) but used as profit? Let's check magnitude.")
    print(f"  d ranges from {d_vals.min():.2f} to {d_vals.max():.2f}.")
    print("  If these were distances in km, typical flight distances are hundreds to thousands; this matches.")
    print("  But lifecycle.py treats d as profit (currency). Could be that the dataset actually stores profit.")
    print("  We need to examine metadata; but from the histogram we can see distribution.")
    
    # Additional: check if d correlates with yd/jd/fd? Already in corr matrix.
    
if __name__ == "__main__":
    main()