"""
Script to analyze if a vehicle can be immobilized and identify any blockers.
Analyzes device status, connectivity, and immobilization requirements.
"""

from main import get_access_token
from device_commands import get_device_status, send_immobilization_command
from datetime import datetime, timedelta


def analyze_immobilization_capability(device_id: str, account: str = None, password: str = None):
    account = account or os.getenv("PROTRACK_ACCOUNT")
    password = password or os.getenv("PROTRACK_PASSWORD")
    
    if not account or not password:
        print("Please provide account and password or set PROTRACK_ACCOUNT/PROTRACK_PASSWORD in .env")
        return
    """
    Analyze if a vehicle can be immobilized and identify any blockers.
    
    Args:
        device_id: Device IMEI number to analyze
        account: Protrack account name
        password: Protrack account password
    """
    print("=" * 70)
    print("Immobilization Capability Analysis")
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
    
    print(f"✓ Access token obtained")
    
    # Step 2: Check device status
    print("\n[Step 2] Analyzing device status...")
    try:
        status_info = get_device_status(access_token, device_id)
        raw_data = status_info.get('raw_data', {})
        
        # Extract detailed timing information
        servertime: Optional[int] = raw_data.get('servertime')
        gpstime: Optional[int] = raw_data.get('gpstime')
        hearttime: Optional[int] = raw_data.get('hearttime')
        systemtime: Optional[int] = raw_data.get('systemtime')
        
        # Calculate time differences
        now = datetime.now().timestamp()
        gps_age: Optional[float] = None
        if gpstime:
            gps_age = now - gpstime
        
        system_age: Optional[float] = None
        if systemtime:
            system_age = now - systemtime
        
        print("\n" + "=" * 70)
        print("Device Status Analysis:")
        print("=" * 70)
        print(f"IMEI:              {status_info.get('imei')}")
        print(f"Connection Status: {status_info.get('status')}")
        print(f"Location:          {status_info.get('location', 'N/A')}")
        print(f"Ignition:          {status_info.get('ignition')}")
        print(f"Current Immobilize Status: {status_info.get('immobilize_status')}")
        
        # Timing information
        print("\n" + "-" * 70)
        print("Timing Information:")
        print("-" * 70)
        if servertime:
            server_dt = datetime.fromtimestamp(servertime)
            print(f"Server Time:       {server_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if gpstime:
            gps_dt = datetime.fromtimestamp(gpstime)
            if gps_age:
                hours_ago = gps_age / 3600
                print(f"Last GPS Data:     {gps_dt.strftime('%Y-%m-%d %H:%M:%S')} ({hours_ago:.1f} hours ago)")
        
        if systemtime:
            system_dt = datetime.fromtimestamp(systemtime)
            if system_age:
                hours_ago = system_age / 3600
                print(f"Device System Time: {system_dt.strftime('%Y-%m-%d %H:%M:%S')} ({hours_ago:.1f} hours ago)")
        
        if hearttime:
            heart_dt = datetime.fromtimestamp(hearttime)
            heart_age = now - hearttime
            hours_ago = heart_age / 3600
            print(f"Last Heartbeat:    {heart_dt.strftime('%Y-%m-%d %H:%M:%S')} ({hours_ago:.1f} hours ago)")
        
        print("=" * 70)
        
        # Analyze immobilization capability
        print("\n" + "=" * 70)
        print("Immobilization Capability Analysis:")
        print("=" * 70)
        
        can_immobilize: bool = True
        blockers: list[str] = []
        warnings: list[str] = []
        
        # Check 1: Device connectivity
        device_status = status_info.get('status')
        if device_status == 'INACTIVE':
            blockers.append(
                f"Device is INACTIVE - No recent data. "
                f"Last GPS data was {gps_age/3600:.1f} hours ago. "
                f"Device must be online to receive commands."
            )
            can_immobilize = False
        elif device_status == 'DELAY':
            warnings.append(
                f"Device has DELAY - Data is stale ({gps_age/3600:.1f} hours old). "
                f"Command may be queued but device may not respond immediately."
            )
        
        # Check 2: Current immobilization status
        current_immobilize = status_info.get('immobilize_status')
        if current_immobilize == 'Immobilized':
            warnings.append("Device is already IMMOBILIZED. Command will be redundant but safe.")
        elif current_immobilize == 'Restored':
            print("✓ Device is currently RESTORED (not immobilized)")
        
        # Check 3: Ignition status
        ignition = status_info.get('ignition')
        if ignition == 'ON':
            warnings.append(
                "Ignition is ON - Vehicle may be running. "
                "Immobilization will stop the engine immediately."
            )
        elif ignition == 'OFF':
            print("✓ Ignition is OFF - Safe to immobilize")
        
        # Check 4: Data freshness
        if gps_age and gps_age > 86400:  # More than 24 hours
            blockers.append(
                f"Device data is very stale ({gps_age/3600:.1f} hours old). "
                f"Device may be powered off, out of coverage, or malfunctioning."
            )
            can_immobilize = False
        
        # Summary
        print("\n" + "-" * 70)
        if can_immobilize:
            print("✓ CAN BE IMMOBILIZED")
            print("\nThe immobilization command can be sent and will:")
            print("  1. Be queued by the Protrack API")
            print("  2. Execute when the device comes online")
            print("  3. Take effect immediately if device is currently online")
        else:
            print("❌ CANNOT BE IMMOBILIZED (at this moment)")
            print("\nThe immobilization command can be sent and queued, but:")
            print("  - Device is currently offline/inactive")
            print("  - Command will execute when device comes back online")
            print("  - Immobilization will take effect at that time")
        
        if warnings:
            print("\n⚠ WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if blockers:
            print("\n🚫 BLOCKERS (Command will be queued, but won't execute until resolved):")
            for blocker in blockers:
                print(f"  - {blocker}")
        
        print("=" * 70)
        
        # Step 3: Test command sending capability
        print("\n[Step 3] Testing command sending capability...")
        try:
            result = send_immobilization_command(access_token, device_id)
            
            if result.get('success'):
                command_id = result.get('raw_response', {}).get('record', {}).get('commandid', 'N/A')
                print("\n" + "=" * 70)
                print("✓ COMMAND SENT SUCCESSFULLY")
                print("=" * 70)
                print(f"Command ID: {command_id}")
                print(f"Status: Command queued in Protrack system")
                
                if not can_immobilize:
                    print("\n⚠ IMPORTANT:")
                    print("  Command is queued but will NOT execute until device comes online.")
                    print("  Monitor device status and wait for it to reconnect.")
                else:
                    print("\n✓ Command should execute soon (device appears to be online)")
                
                print("=" * 70)
            else:
                print(f"\n❌ Command sending failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"\n❌ Error sending command: {str(e)}")
            print("\nThis could indicate:")
            print("  - Device not found in account")
            print("  - Device doesn't support immobilization commands")
            print("  - Authentication/authorization issues")
            print("  - Network/API connectivity problems")
        
    except Exception as e:
        print(f"\n❌ Error analyzing device: {str(e)}")
        return


if __name__ == "__main__":
    # Device ID to analyze
    device_id: str = "355710091063524"
    
    # Protrack account credentials
    account: str = os.getenv("PROTRACK_ACCOUNT")
    password: str = os.getenv("PROTRACK_PASSWORD")
    
    # Run the analysis
    analyze_immobilization_capability(device_id, account, password)
