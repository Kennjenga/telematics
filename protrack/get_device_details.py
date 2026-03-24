import os
import sys
import json
import requests
from main import get_access_token
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_device_details(imei: str):
    account = os.getenv("PROTRACK_ACCOUNT")
    password = os.getenv("PROTRACK_PASSWORD")
    
    print("=" * 70)
    print(f"Protrack Device Details for IMEI: {imei}")
    print("=" * 70)
    
    token = get_access_token(account, password)
    if not token:
        return

    # Protrack usually provides details via /api/device/info
    url = f"https://api.protrack365.com/api/device/info?access_token={token}&imei={imei}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            # Protrack often nests data in a 'data' array or 'record' object
            details = data.get("data", data.get("record", {}))
            print(json.dumps(details, indent=4))
        else:
            print(f"Failed to get details: {data.get('message')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_device_details.py <IMEI>")
        sys.exit(1)
        
    get_device_details(sys.argv[1])
