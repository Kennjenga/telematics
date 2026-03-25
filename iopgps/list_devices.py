import os
import json
import requests
from main import get_access_token
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def list_account_devices():
    app_id = os.getenv("IOPGPS_APPID")
    app_key = os.getenv("IOPGPS_APPKEY")
    
    print("=" * 70)
    print(f"Listing Devices for Account: {app_id}")
    print("=" * 70)
    
    token = get_access_token(app_id, app_key)
    if not token:
        return

    # Use GET /api/device to list devices for the account
    # pageSize can be up to 100
    url = f"https://open.iopgps.com/api/device?pageSize=100"
    headers = {"accessToken": token}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            devices = data.get("data", [])
            print(f"Total Device Count: {len(devices)}")
            print("-" * 70)
            for dev in devices:
                imei = dev.get("imei")
                name = dev.get("name", "Unnamed")
                # Showing more data as requested
                status = dev.get("status", "N/A")
                print(f"IMEI: {imei:16} | Name: {name:15} | Status: {status}")
        else:
            print(f"Failed to list devices: {data.get('result')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_account_devices()
