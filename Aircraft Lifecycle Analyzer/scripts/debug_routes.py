#!/usr/bin/env python3
"""
Data probe for route dataset.
Prints columns, sample data, and unique values for aircraft, origin, destination.
Also checks for specific values: A220-100, PEK, SIN.
"""
import sys
import os

# Add the analysis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis'))

from datasets import dataset_service

def main():
    # Load the route data
    route_df = dataset_service.get_route()
    print("=== Route DataFrame Info ===")
    print(f"Shape: {route_df.shape}")
    print("\nColumns:")
    print(route_df.columns.tolist())
    print("\nFirst 5 rows:")
    print(route_df.head())
    
    # Load aircraft and airports to map IDs to names/codes
    aircraft_df = dataset_service.get_aircraft()
    airports_df = dataset_service.get_airport()
    
    print("\n=== Aircraft Info (first 50 unique shortnames) ===")
    # We don't have shortname in route_df, but we can check the aircraft dataset
    unique_ac_shortnames = aircraft_df['shortname'].unique()
    print(f"Total unique aircraft: {len(unique_ac_shortnames)}")
    print("First 50:", unique_ac_shortnames[:50])
    
    print("\n=== Origin Airport Info (first 20 unique IATA) ===")
    unique_origin_iata = airports_df['iata'].unique()
    print(f"Total unique airports: {len(unique_origin_iata)}")
    print("First 20:", unique_origin_iata[:20])
    
    print("\n=== Destination Airport Info (first 20 unique IATA) ===")
    # Same as origin for airports
    print("First 20:", unique_origin_iata[:20])
    
    # Now, check for specific values in the aircraft and airports datasets
    print("\n=== Specific Value Checks ===")
    # Check aircraft
    ac_check = 'A220-100'
    ac_found = ac_check in aircraft_df['shortname'].values
    print(f"Aircraft '{ac_check}' exists in aircraft dataset: {ac_found}")
    
    # Check airports
    origin_check = 'PEK'
    dest_check = 'SIN'
    origin_found = origin_check in airports_df['iata'].values
    dest_found = dest_check in airports_df['iata'].values
    print(f"Origin '{origin_check}' exists in airports dataset: {origin_found}")
    print(f"Destination '{dest_check}' exists in airports dataset: {dest_found}")
    
    # If we want to check if a route exists, we need to get the IDs and then look in routes
    if ac_found and origin_found and dest_found:
        ac_id = aircraft_df.loc[aircraft_df['shortname'] == ac_check, 'id'].iloc[0]
        origin_id = airports_df.loc[airports_df['iata'] == origin_check, 'id'].iloc[0]
        dest_id = airports_df.loc[airports_df['iata'] == dest_check, 'id'].iloc[0]
        
        # Look for route in the route dataset
        route_exists = dataset_service.find_routes(aircraft_id=ac_id, origin_id=origin_id, dest_id=dest_id)
        reverse_route_exists = dataset_service.find_routes(aircraft_id=ac_id, origin_id=dest_id, dest_id=origin_id)
        
        print(f"\nRoute {ac_check} from {origin_check} to {dest_check} exists: {not route_exists.empty}")
        print(f"Reverse route {ac_check} from {dest_check} to {origin_check} exists: {not reverse_route_exists.empty}")
    else:
        print("\nSkipping route existence check due to missing aircraft or airport.")

if __name__ == '__main__':
    main()