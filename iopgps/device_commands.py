import requests
from typing import Dict, Any

BASE_URL = "https://open.iopgps.com"

def get_device_status(access_token: str, device_id: str) -> Dict[str, Any]:
    """
    Get device status via GET /api/device/status
    """
    url = f"{BASE_URL}/api/device/status?imei={device_id}"
    headers = {"accessToken": access_token}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # Defaults
    status_dict = {
        "imei": device_id,
        "status": "INACTIVE",
        "ignition": False,
        "immobilize_status": "Normal",
        "last_sync": "Unknown"
    }
    
    if data.get("code") == 0 and data.get("data"):
        record = data["data"][0]  # usually returns list
        
        # Example mappings (assuming standard JSON properties from their docs)
        # 1 = Online/moving, 2 = Static, 3 = Offline 
        raw_status = str(record.get("status", ""))
        if raw_status in ["1", "2"]:
            status_dict["status"] = "ACTIVE"
        
        # Acc mapping (assuming acc=1 is ON)
        status_dict["ignition"] = bool(record.get("acc", 0))
        
        # Oil/power mapping (usually 0 is cutoff)
        oil_status = record.get("oil", 1)  # using fallback to normal
        if oil_status == 0:
            status_dict["immobilize_status"] = "Immobilized"
            
        status_dict["last_sync"] = record.get("gpsTime", "Unknown")
        
    return status_dict

def send_immobilization_command(access_token: str, device_id: str, action: str = "2") -> Dict[str, Any]:
    """
    Send immobilize/restore command via POST /api/instruction/relay.
    action="2" -> Cut oil/electricity (Immobilize)
    action="1" -> Restore oil/electricity
    """
    url = f"{BASE_URL}/api/instruction/relay"
    headers = {"accessToken": access_token}
    payload = {
        "parameter": action,
        "imeis": [device_id]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    is_success = data.get("code") == 0
    return {
        "success": is_success,
        "message": data.get("result", "Success" if is_success else "Unknown error"),
        "device_id": device_id,
        "uuid": data.get("details", [{}])[0].get("uuid") if is_success else None
    }
    
def check_command_result(access_token: str, uuid: str) -> Dict[str, Any]:
    """
    Check the async result of the immobilize command via GET /api/instruction/relay
    """
    url = f"{BASE_URL}/api/instruction/relay?uuid={uuid}"
    headers = {"accessToken": access_token}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
