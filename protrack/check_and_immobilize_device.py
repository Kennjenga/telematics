"""
Script to check device status and send immobilization command for a specific device.
Usage: python3 check_and_immobilize_device.py
"""

from main import get_access_token
from device_commands import get_device_status, send_immobilization_command


def check_and_immobilize_device(device_id: str, account: str = None, password: str = None):
    # Fallback to .env if not provided
    account = account or os.getenv("PROTRACK_ACCOUNT")
    password = password or os.getenv("PROTRACK_PASSWORD")
    
    if not account or not password:
        print("Please provide account and password or set PROTRACK_ACCOUNT/PROTRACK_PASSWORD in .env")
        return
    """
    Check device status and send immobilization command if needed.
    
    Args:
        device_id: Device IMEI number to check and immobilize
        account: Protrack account name 
        password: Protrack account password 
    """
    print("=" * 70)
    print("Device Status Check and Immobilization")
    print("=" * 70)
    print(f"Device ID (IMEI): {device_id}")
    print(f"Account: {account}")
    print("-" * 70)
    
    # Step 1: Get access token
    print("\n[Step 1] Getting access token...")
    access_token: str = get_access_token(account, password)
    
    if not access_token:
        print("❌ Failed to get access token. Exiting.")
        return
    
    print(f"✓ Access token obtained: {access_token[:20]}...")
    
    # Step 2: Check device status
    print("\n[Step 2] Checking device status...")
    try:
        status_info = get_device_status(access_token, device_id)
        
        print("\n" + "=" * 70)
        print("Device Status Information:")
        print("=" * 70)
        print(f"IMEI:              {status_info.get('imei')}")
        print(f"Status:            {status_info.get('status')}")
        print(f"Last Sync:         {status_info.get('last_sync', 'N/A')}")
        print(f"Location:          {status_info.get('location', 'N/A')}")
        print(f"Ignition:          {status_info.get('ignition')}")
        print(f"Immobilize Status: {status_info.get('immobilize_status')}")
        mileage = status_info.get('mileage')
        if mileage is not None:
            print(f"Mileage:           {mileage} km")
        else:
            print(f"Mileage:           N/A")
        print("=" * 70)
        
        # Check for potential issues
        issues: list[str] = []
        if status_info.get('status') == 'INACTIVE':
            issues.append("Device is INACTIVE (no recent data)")
        elif status_info.get('status') == 'DELAY':
            issues.append("Device has DELAY (data is stale)")
        
        if status_info.get('immobilize_status') == 'Immobilized':
            issues.append("Device is already IMMOBILIZED")
        
        if issues:
            print("\n⚠ Potential Issues Detected:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ No obvious issues detected")
        
    except Exception as e:
        print(f"\n❌ Error checking device status: {str(e)}")
        print("\nThis could indicate:")
        print("  - Device not found in the account")
        print("  - Authentication issues")
        print("  - Network/API connectivity problems")
        return
    
    # Step 3: Send immobilization command
    print("\n[Step 3] Sending immobilization command...")
    try:
        result = send_immobilization_command(access_token, device_id)
        
        if result.get('success'):
            print("\n" + "=" * 70)
            print("✓ IMMOBILIZATION COMMAND SENT SUCCESSFULLY")
            print("=" * 70)
            print(f"Device ID: {result.get('device_id')}")
            print(f"Message:   {result.get('message')}")
            print("=" * 70)
        else:
            print(f"\n❌ Immobilization command failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error sending immobilization command: {str(e)}")
        print("\nThis could indicate:")
        print("  - Device not found")
        print("  - Device does not support immobilization commands")
        print("  - Authentication/authorization issues")
        print("  - Network/API connectivity problems")


if __name__ == "__main__":
    # Device ID to check and immobilize
    device_id: str = "355710091063524"
    
    # Protrack account credentials (update if needed)
    account: str = os.getenv("PROTRACK_ACCOUNT")
    password: str = os.getenv("PROTRACK_PASSWORD")
    
    # Run the check and immobilization
    check_and_immobilize_device(device_id, account, password)
