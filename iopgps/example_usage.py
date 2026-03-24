#!/usr/bin/env python3
import os
from dotenv import load_dotenv, find_dotenv
from main import get_access_token
from fetch_mileage import fetch_vehicle_mileage, save_mileage_data_to_json

load_dotenv(find_dotenv())

def run_example():
    appid = os.getenv("IOPGPS_APPID")
    password = os.getenv("IOPGPS_PASSWORD")
    
    if not appid or not password:
        print("Environment variables missing!")
        return
        
    token = get_access_token(appid, password)
    if not token:
        return
        
    device_id = "355710091063524"  # Replace with actual
    
    print(f"\nFetching mileage for {device_id}...")
    mileage_data = fetch_vehicle_mileage(token, device_id, "2025-01-01", "2025-01-02")
    
    if mileage_data:
        for rec in mileage_data:
            print(f"IMEI: {rec['imei']}")
            print(f"Mileage Driven: {rec['mileage']} km")
        save_mileage_data_to_json(mileage_data, "iopgps_mileage_data.json")
    else:
        print("No mileage data returned.")

if __name__ == "__main__":
    run_example()
