import os
import sys
import json
import requests
from main import get_access_token
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_device_details(imei: str):
    app_id = os.getenv("IOPGPS_APPID")
    app_key = os.getenv("IOPGPS_APPKEY")
    
    print("=" * 70)
    print(f"IOPGPS Device Details for IMEI: {imei}")
    print("=" * 70)
    
    token = get_access_token(app_id, app_key)
    if not token:
        return

    # Using GET /api/device/detail (as per user-provided Open API specs)
    url = f"https://open.iopgps.com/api/device/detail?imei={imei}"
    headers = {"accessToken": token}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            print(json.dumps(data.get("data", {}), indent=4))
        else:
            print(f"Failed to get details: {data.get('message')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_device_details.py <IMEI>")
        sys.exit(1)
        
    get_device_details(sys.argv[1])
