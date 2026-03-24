import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def fetch_vehicle_mileage(access_token: str, device_id: str, start_time: str, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch mileage using GET /api/device/miles
    start_time and end_time should be ISO datetime strings or timestamps, depending on API requirements.
    Docs say: Start time, timestamp, unit seconds
    """
    
    # Convert string dates to timestamps (assuming naive format YYYY-MM-DD for simplicity)
    try:
        start_ts = int(datetime.strptime(start_time, "%Y-%m-%d").timestamp())
        if end_time:
            end_ts = int(datetime.strptime(end_time, "%Y-%m-%d").timestamp())
        else:
            end_ts = int(datetime.now().timestamp())
    except Exception as e:
        print(f"Date parsed failed: {e}")
        return []

    url = f"https://open.iopgps.com/api/device/miles?imei={device_id}&startTime={start_ts}&endTime={end_ts}"
    headers = {"accessToken": access_token}
    
    print(f"Requesting mileage URL: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    results = []
    if data.get("code") == 0:
        miles = data.get("miles", 0.0)
        runtime = data.get("runTime", 0)
        results.append({
            "imei": device_id,
            "mileage": miles,
            "runtime_seconds": runtime,
            "begin_date": start_time,
            "end_date": end_time
        })
    return results

def save_mileage_data_to_json(data: List[Dict], filename: str = "mileage_data.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Saved {len(data)} records to {filename}")
