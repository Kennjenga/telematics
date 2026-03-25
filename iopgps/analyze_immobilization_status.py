"""
Script to analyze if an IOPGPS device can be immobilized.
"""
import os
from dotenv import load_dotenv, find_dotenv
from main import get_access_token
from device_commands import get_device_status

load_dotenv(find_dotenv())

def analyze_immobilization_capability(device_id: str, app_id: str = None, app_key: str = None):
    app_id = app_id or os.getenv("IOPGPS_APPID")
    app_key = app_key or os.getenv("IOPGPS_APPKEY")
    
    if not app_id or not app_key:
        print("Please provide app_id and app_key or set IOPGPS_APPID/IOPGPS_APPKEY in .env")
        return
        
    print(f"Analyzing Immobilization Capability for {device_id}...")
    token = get_access_token(app_id, app_key)
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
