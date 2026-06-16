#!/usr/bin/env python3
"""
Route Coverage Analysis script for AM4user project.

This script analyzes the route.parquet dataset to provide:
1. Count of routes per aircraft (fd)
2. Specific counts for A220-100 (fd=322), PEK (jd=3890), SIN (yd=3731)
3. Intersection counts to see where filters eliminate records.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.datasets import dataset_service
import pandas as pd

def main():
    # Load route data
    routes = dataset_service.routes
    print(f"Total routes in dataset: {len(routes)}")
    print("="*60)

    # 1. Count routes per aircraft (fd) - general
    aircraft_df = dataset_service.aircraft[['id', 'shortname']].copy()
    aircraft_df.set_index('id', inplace=True)
    routes_with_ac = routes.join(aircraft_df, on='fd', how='left')
    ac_counts = routes_with_ac['shortname'].value_counts()

    # Output requested format for specific aircraft
    print("Aircraft     RouteCount")
    # Map aircraft names to shortnames as they appear in dataset
    # A220-100 -> shortname a221
    # B738 -> shortname b738
    # A320neo -> shortname a32neo
    target_map = {
        "A220-100": "a221",
        "B738": "b738",
        "A320neo": "a32neo",
    }
    for name, short in target_map.items():
        count = ac_counts.get(short, 0)
        print(f"{short:<12} {count}")
    print("-" * 60)

    # Additional insight: distribution statistics
    print("Distribution of routes per aircraft:")
    print(f"  Min: {ac_counts.min()}")
    print(f"  Max: {ac_counts.max()}")
    print(f"  Mean: {ac_counts.mean():.0f}")
    print(f"  Std: {ac_counts.std():.0f}")
    print("-" * 60)

    # 2. Specific counts
    # A220-100: fd == 322
    fd_322 = routes[routes['fd'] == 322]
    count_fd_322 = len(fd_322)
    print(f"2. Routes where fd == 322 (A220-100): {count_fd_322}")

    # PEK: jd == 3890
    jd_3890 = routes[routes['jd'] == 3890]
    count_jd_3890 = len(jd_3890)
    print(f"3. Routes where jd == 3890 (PEK as origin): {count_jd_3890}")

    # SIN: yd == 3731
    yd_3731 = routes[routes['yd'] == 3731]
    count_yd_3731 = len(yd_3731)
    print(f"4. Routes where yd == 3731 (SIN as destination): {count_yd_3731}")

    # 5. Intersections
    # fd == 322 & jd == 3890
    fd_jd = routes[(routes['fd'] == 322) & (routes['jd'] == 3890)]
    count_fd_jd = len(fd_jd)
    print(f"5a. Routes where fd == 322 AND jd == 3890: {count_fd_jd}")

    # fd == 322 & yd == 3731
    fd_yd = routes[(routes['fd'] == 322) & (routes['yd'] == 3731)]
    count_fd_yd = len(fd_yd)
    print(f"5b. Routes where fd == 322 AND yd == 3731: {count_fd_yd}")

    # Optional: jd == 3890 & yd == 3731 (route PEK->SIN regardless of aircraft)
    jd_yd = routes[(routes['jd'] == 3890) & (routes['yd'] == 3731)]
    count_jd_yd = len(jd_yd)
    print(f"5c. Routes where jd == 3890 AND yd == 3731 (PEK->SIN): {count_jd_yd}")

    # If there are matches, show examples
    if count_fd_jd > 0:
        print("\nExample records for fd=322 & jd=3890:")
        print(fd_jd.head())
    if count_fd_yd > 0:
        print("\nExample records for fd=322 & yd=3731:")
        print(fd_yd.head())
    if count_jd_yd > 0:
        print("\nExample records for jd=3890 & yd=3731 (PEK->SIN):")
        print(jd_yd.head())

if __name__ == "__main__":
    main()