"""
Script to check device status and send immobilization command for IOPGPS.
"""
import os
from dotenv import load_dotenv, find_dotenv
from main import get_access_token
from device_commands import get_device_status, send_immobilization_command

load_dotenv(find_dotenv())

def check_and_immobilize_device(device_id: str, app_id: str = None, app_key: str = None):
    app_id = app_id or os.getenv("IOPGPS_APPID")
    app_key = app_key or os.getenv("IOPGPS_APPKEY")
    
    if not app_id or not app_key:
        print("Please provide app_id and app_key or set IOPGPS_APPID/IOPGPS_APPKEY in .env")
        return

    print("=" * 70)
    print("Device Status Check and Immobilization (IOPGPS)")
    print("=" * 70)
    print(f"Device ID: {device_id}")
    print(f"AppID: {app_id}")
    print("-" * 70)
    
    print("\n[Step 1] Getting access token...")
    access_token = get_access_token(app_id, app_key)
    if not access_token:
        print("❌ Failed to get access token. Exiting.")
        return
    
    print(f"✓ Access token obtained: {access_token[:15]}...")
    
    print("\n[Step 2] Checking device status...")
    try:
        status_info = get_device_status(access_token, device_id)
        
        print("\n" + "=" * 70)
        print("Device Status Information:")
        print("=" * 70)
        print(f"IMEI:              {status_info.get('imei')}")
        print(f"Status:            {status_info.get('status')}")
        print(f"Last Sync:         {status_info.get('last_sync')}")
        print(f"Ignition:          {status_info.get('ignition')}")
        print(f"Immobilize Status: {status_info.get('immobilize_status')}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error checking device status: {str(e)}")
        return
    
    print("\n[Step 3] Sending immobilization command (Cut Oil/Electricity)...")
    try:
        # Action "2" is cut oil/electricity in IOPGPS
        result = send_immobilization_command(access_token, device_id, action="2")
        
        if result.get('success'):
            print("\n" + "=" * 70)
            print("✓ IMMOBILIZATION COMMAND SENT SUCCESSFULLY")
            print("=" * 70)
            print(f"UUID:      {result.get('uuid')}")
            print(f"Message:   {result.get('message')}")
            print("=" * 70)
        else:
            print(f"\n❌ Immobilization command failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error sending immobilization command: {str(e)}")

if __name__ == "__main__":
    test_device_id = "355710091063524"  # Default test IMEI
    check_and_immobilize_device(test_device_id)
