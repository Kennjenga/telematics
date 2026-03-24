"""
Script to analyze if an IOPGPS device can be immobilized.
"""
import os
from dotenv import load_dotenv, find_dotenv
from main import get_access_token
from device_commands import get_device_status

load_dotenv(find_dotenv())

def analyze_immobilization_capability(device_id: str, appid: str = None, password: str = None):
    appid = appid or os.getenv("IOPGPS_APPID")
    password = password or os.getenv("IOPGPS_PASSWORD")
    
    if not appid or not password:
        print("Please provide appid and password or set IOPGPS_APPID/IOPGPS_PASSWORD in .env")
        return
        
    print(f"Analyzing Immobilization Capability for {device_id}...")
    token = get_access_token(appid, password)
    if not token:
        print("❌ Auth failed")
        return
        
    status_info = get_device_status(token, device_id)
    
    is_active = status_info.get("status") == "ACTIVE"
    # Wait, IOPGPS can immobilize depending on the user's discretion, no specific strict vehicle safety checks locally
    
    print("\n--- Summary ---")
    print(f"Device Status: {status_info.get('status')}")
    print(f"Ignition: {status_info.get('ignition')}")
    print(f"Already Immobilized: {status_info.get('immobilize_status') == 'Immobilized'}")
    
    if not is_active:
        print("⚠ Device is not purely ACTIVE, immobilization may be queued or fail.")

if __name__ == "__main__":
    analyze_immobilization_capability("355710091063524")
