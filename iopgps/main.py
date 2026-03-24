import time
import hashlib
import requests
import os
from typing import Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def calculate_signature(password: str, current_time: int) -> str:
    md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    combined_string = md5_password + str(current_time)
    return hashlib.md5(combined_string.encode('utf-8')).hexdigest()

def get_access_token(appid: str, password: str) -> Optional[str]:
    """
    Authenticate against IOPGPS using POST /api/auth.
    """
    current_time = int(time.time())
    signature = calculate_signature(password, current_time)
    
    url = "https://open.iopgps.com/api/auth"
    payload = {
        "appid": appid,
        "time": current_time,
        "signature": signature
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and "accessToken" in data:
            return data["accessToken"]
        else:
            print(f"Auth failed: {data}")
            return None
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None

if __name__ == "__main__":
    appid = os.getenv("IOPGPS_APPID")
    password = os.getenv("IOPGPS_PASSWORD")
    if not appid or not password:
        print("Please configure IOPGPS_APPID and IOPGPS_PASSWORD in .env")
    else:
        print(f"Testing auth for {appid}...")
        token = get_access_token(appid, password)
        if token:
            print(f"Success! Token: {token[:15]}...")
