import os
import json
import requests
from main import get_access_token
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def list_protrack_devices():
    # Attempting to fetch devices from Protrack
    # Note: Protrack API typically uses a 'tracking' or 'get_devices' endpoint.
    account = os.getenv("PROTRACK_ACCOUNT")
    password = os.getenv("PROTRACK_PASSWORD")
    
    print("=" * 70)
    print(f"Listing Protrack Devices for Account: {account}")
    print("=" * 70)
    
    token = get_access_token(account, password)
    if not token:
        return

    # Protrack usually lists all devices via /api/track without specific IMEIs
    # or via a specific device list endpoint like /api/device/list
    url = f"https://api.protrack365.com/api/track?access_token={token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            devices = data.get("record", [])
            print(f"Total Device Count: {len(devices)}")
            print("-" * 70)
            for dev in devices:
                imei = dev.get("imei")
                name = dev.get("name", "Unnamed")
                status = dev.get("status", "Unknown")
                print(f"IMEI: {imei} | Name: {name} | Status: {status}")
        else:
            print(f"Failed to list devices: {data.get('message')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_protrack_devices()
