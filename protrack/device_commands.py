"""
Module to send commands to Protrack devices and check device status.
Supports immobilization (RELAY,1) and restoration (RELAY,0) commands.
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
from main import get_access_token


def get_device_status(access_token: str, imei: str) -> Dict[str, Any]:
    """
    Get device status from Protrack API using the track endpoint.
    
    Args:
        access_token: Protrack API access token
        imei: Device IMEI number
    
    Returns:
        Dictionary containing device status information including:
        - status: Device status (ACTIVE, INACTIVE, DELAY)
        - last_sync: Last synchronization datetime
        - location: Current location (latitude, longitude)
        - ignition: Ignition status (ON, OFF, UNKNOWN)
        - immobilize_status: Immobilization status (Immobilized, Restored, Unknown)
        - mileage: Current mileage in kilometers
        - raw_data: Raw response from API
    
    Raises:
        requests.RequestException: If API request fails
        ValueError: If device not found or API returns error
    """
    # Construct the API URL for track endpoint
    url: str = "https://api.protrack365.com/api/track"
    params: Dict[str, str] = {
        'access_token': access_token,
        'imeis': imei
    }
    
    print(f"Checking device status for IMEI: {imei}")
    print(f"Request URL: {url}")
    print(f"Parameters: access_token=***, imeis={imei}")
    
    try:
        # Send GET request to Protrack API
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raises an error for HTTP error codes
        data: Dict[str, Any] = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {data}")
        
        # Check API response code
        api_code: int = data.get("code", -1)
        if api_code != 0:
            error_message: str = data.get("message", "Unknown error")
            raise ValueError(
                f"Protrack API error (code {api_code}): {error_message}"
            )
        
        # Extract device records from response
        records: list = data.get("record", [])
        if not records:
            raise ValueError(f"No device data found for IMEI {imei}")
        
        # Get the first record (should be the device we're looking for)
        device_record: Dict[str, Any] = records[0]
        
        # Extract device information
        device_imei: str = str(device_record.get("imei", imei))
        
        # Get timestamp and convert to datetime
        # Try multiple timestamp fields (servertime is most accurate, then hearttime, then gpstime)
        timestamp: Optional[int] = (
            device_record.get("servertime") or 
            device_record.get("hearttime") or 
            device_record.get("gpstime") or 
            device_record.get("time")
        )
        last_sync: Optional[datetime] = None
        if timestamp:
            try:
                last_sync = datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                pass
        
        # Determine device status based on last sync time
        status: str = "INACTIVE"
        if last_sync:
            time_diff = datetime.now() - last_sync
            if time_diff.total_seconds() < 300:  # Less than 5 minutes
                status = "ACTIVE"
            elif time_diff.total_seconds() < 1800:  # Less than 30 minutes
                status = "DELAY"
        
        # Get location
        latitude: Optional[float] = device_record.get("latitude")
        longitude: Optional[float] = device_record.get("longitude")
        location: Optional[str] = None
        if latitude is not None and longitude is not None:
            location = f"{latitude},{longitude}"
        
        # Get ignition status (accstatus: 1=ON, 0=OFF, -1=UNKNOWN)
        accstatus: int = device_record.get("accstatus", -1)
        ignition: str = "UNKNOWN"
        if accstatus == 1:
            ignition = "ON"
        elif accstatus == 0:
            ignition = "OFF"
        
        # Get immobilization status (oilpowerstatus: 1=Restored, 0=Immobilized, -1=Unknown)
        oilpowerstatus: int = device_record.get("oilpowerstatus", -1)
        immobilize_status: str = "Unknown"
        if oilpowerstatus == 1:
            immobilize_status = "Restored"
        elif oilpowerstatus == 0:
            immobilize_status = "Immobilized"
        
        # Get mileage (in kilometers)
        mileage: Optional[float] = device_record.get("mileage")
        if mileage is not None and mileage < 0:
            mileage = None  # Invalid mileage
        
        # Build status dictionary
        status_info: Dict[str, Any] = {
            "imei": device_imei,
            "status": status,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "location": location,
            "ignition": ignition,
            "immobilize_status": immobilize_status,
            "mileage": mileage,
            "raw_data": device_record
        }
        
        return status_info
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to get device status from Protrack API: {str(e)}"
        )


def send_immobilization_command(access_token: str, imei: str) -> Dict[str, Any]:
    """
    Send immobilization command (RELAY,1) to a Protrack device.
    
    Args:
        access_token: Protrack API access token
        imei: Device IMEI number
    
    Returns:
        Dictionary containing command result:
        - success: Boolean indicating if command was sent successfully
        - message: Status message
        - device_id: Device IMEI
        - raw_response: Raw API response
    
    Raises:
        requests.RequestException: If API request fails
        ValueError: If device not found or API returns error
    """
    # Construct the API URL for command send endpoint
    url: str = "https://api.protrack365.com/api/command/send"
    params: Dict[str, str] = {
        'access_token': access_token,
        'imei': imei,
        'command': 'RELAY,1'  # RELAY,1 = Immobilize, RELAY,0 = Restore
    }
    
    print(f"Sending immobilization command to IMEI: {imei}")
    print(f"Request URL: {url}")
    print(f"Parameters: access_token=***, imei={imei}, command=RELAY,1")
    
    try:
        # Send POST request to Protrack API
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()  # Raises an error for HTTP error codes
        data: Dict[str, Any] = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {data}")
        
        # Check API response code (Protrack docs: https://www.protrack365.com/api.html §3)
        api_code: int = data.get("code", -1)
        if api_code != 0:
            error_message: str = data.get("message", "Unknown error")
            error_code: int = api_code
            
            # Map Protrack error codes to accurate descriptions
            if error_code == 10001:  # Target doesn't exist
                raise ValueError(f"Device {imei} not found")
            elif error_code == 10012:  # Access token is out of date
                raise ValueError(
                    f"Access token expired (code {error_code}). "
                    f"Please get a fresh access token and try again."
                )
            elif error_code == 20017:  # Device is offline
                raise ValueError(
                    f"Device is offline (code 20017): {error_message}. "
                    f"Ensure the tracker has power and signal, then try again."
                )
            elif error_code == 20018:  # Send command fail
                raise ValueError(
                    f"Send command failed (code 20018): {error_message}. "
                    f"The device may not support immobilization or the command could not reach the device."
                )
            else:
                raise ValueError(
                    f"Protrack API error (code {error_code}): {error_message}"
                )
        
        # Command sent successfully
        result: Dict[str, Any] = {
            "success": True,
            "message": "Immobilization command sent successfully",
            "device_id": imei,
            "raw_response": data
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to send immobilization command to Protrack API: {str(e)}"
        )


def send_restore_command(access_token: str, imei: str) -> Dict[str, Any]:
    """
    Send restore command (RELAY,0) to a Protrack device.
    
    Args:
        access_token: Protrack API access token
        imei: Device IMEI number
    
    Returns:
        Dictionary containing command result:
        - success: Boolean indicating if command was sent successfully
        - message: Status message
        - device_id: Device IMEI
        - raw_response: Raw API response
    
    Raises:
        requests.RequestException: If API request fails
        ValueError: If device not found or API returns error
    """
    # Construct the API URL for command send endpoint
    url: str = "https://api.protrack365.com/api/command/send"
    params: Dict[str, str] = {
        'access_token': access_token,
        'imei': imei,
        'command': 'RELAY,0'  # RELAY,0 = Restore, RELAY,1 = Immobilize
    }
    
    print(f"Sending restore command to IMEI: {imei}")
    print(f"Request URL: {url}")
    print(f"Parameters: access_token=***, imei={imei}, command=RELAY,0")
    
    try:
        # Send POST request to Protrack API
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()  # Raises an error for HTTP error codes
        data: Dict[str, Any] = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {data}")
        
        # Check API response code (Protrack docs: https://www.protrack365.com/api.html §3)
        api_code: int = data.get("code", -1)
        if api_code != 0:
            error_message: str = data.get("message", "Unknown error")
            error_code: int = api_code
            
            # Map Protrack error codes to accurate descriptions
            if error_code == 10001:  # Target doesn't exist
                raise ValueError(f"Device {imei} not found")
            elif error_code == 10012:  # Access token is out of date
                raise ValueError(
                    f"Access token expired (code {error_code}). "
                    f"Please get a fresh access token and try again."
                )
            elif error_code == 20017:  # Device is offline
                raise ValueError(
                    f"Device is offline (code 20017): {error_message}. "
                    f"Ensure the tracker has power and signal, then try again."
                )
            elif error_code == 20018:  # Send command fail
                raise ValueError(
                    f"Send command failed (code 20018): {error_message}. "
                    f"The device may not support the command or it could not reach the device."
                )
            else:
                raise ValueError(
                    f"Protrack API error (code {error_code}): {error_message}"
                )
        
        # Command sent successfully
        result: Dict[str, Any] = {
            "success": True,
            "message": "Restore command sent successfully",
            "device_id": imei,
            "raw_response": data
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to send restore command to Protrack API: {str(e)}"
        )
