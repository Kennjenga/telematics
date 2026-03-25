import time
import hashlib
import requests
import os
from dotenv import load_dotenv, find_dotenv
from typing import Optional

load_dotenv(find_dotenv())

BASE_URL = "https://open.iopgps.com"

def calculate_signature(secret_key: str, current_time: int) -> str:
    md5_key = hashlib.md5(secret_key.encode('utf-8')).hexdigest()
    combined_string = md5_key + str(current_time)
    return hashlib.md5(combined_string.encode('utf-8')).hexdigest()

import json

def get_access_token(app_id: str, app_key: str) -> Optional[str]:
    """
    Authenticate against IOPGPS using APPID and APPKEY.
    """
    # 1. Try the user-suggested /api/login endpoint without signature
    url_login = f"{BASE_URL}/api/login"
    payload_login = {
        "appId": app_id,
        "appKey": app_key
    }
    
    try:
        r = requests.post(url_login, json=payload_login, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == 200 and "result" in data and "accessToken" in data["result"]:
                return data["result"]["accessToken"]
    except Exception:
        pass
        
    # 2. Try the officially documented /api/auth endpoint with MD5 signature
    url_auth = f"{BASE_URL}/api/auth"
    current_time = int(time.time())
    signature = calculate_signature(app_key, current_time)
    
    payload_auth = {
        "appid": app_id,
        "time": current_time,
        "signature": signature
    }
    
    try:
        response = requests.post(url_auth, json=payload_auth, timeout=30)
        
        if response.status_code == 404:
            print(f"Error authenticating: 404 Client Error for both {url_login} and {url_auth}")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and "accessToken" in data:
            return data["accessToken"]
        else:
            print(f"Auth failed on {url_auth}: {data}")
            return None
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None


if __name__ == "__main__":
    app_id = os.getenv("IOPGPS_APPID")
    app_key = os.getenv("IOPGPS_APPKEY")
    if not app_id or not app_key:
        print("Please configure IOPGPS_APPID and IOPGPS_APPKEY in telematics/.env")
    else:
        print(f"Testing auth for {app_id}...")
        token = get_access_token(app_id, app_key)
        if token:
            print(f"Success! Token: {token[:15]}...")

