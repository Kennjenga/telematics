# Protrack Standalone Testing Module

This module provides standalone scripts for interacting with the Protrack API via `https://api.protrack365.com`.

## 🚀 API Endpoint Reference

| Command / File | Endpoint | Method | Key Headers/Params | Response Highlights |
| :--- | :--- | :---: | :--- | :--- |
| **`main.py`** | `/api/authorization` | `GET` | `account`, `signature`, `time` | `access_token`, `expires_in` |
| **`list_devices.py`** | `/api/track` | `GET` | `access_token` | `record` (List of active devices), `code` |
| **`get_device_details.py`** | `/api/device/info` | `GET` | `imei`, `access_token` | `record` (Hardware version, ICCID, expiry) |
| **`fetch_mileage.py`** | `/api/mileage` | `GET` | `imeis`, `begintime`, `endtime`, `access_token` | `record` (Total mileage for range) |
| **`device_commands.py`** | `/api/track` | `GET` | `imeis`, `access_token` | `accstatus`, `oilpowerstatus` |
| **`check_and_immobilize_device.py`**| `/api/relay` | `GET` | `type`: "cutoff", `imeis`, `access_token` | `code`, `message`, `uuid` |

---

## 📂 File Explanations

### **Core Logic**
- **`main.py`**: Handles Protrack-specific authentication logic. It uses the `account` and `password` to generate a signature and returns the JWT Bearer token needed for all requests.
- **`device_commands.py`**: Implements the relay command logic. It specifically maps the "cutoff" and "restore" command types to the Protrack API format.

### **Discovery & Data**
- **`list_devices.py`**: Fetches every device currently active in the Protrack account. Useful for verifying device registration and matching IMEIs with license plates.
- **`get_device_details.py`**: Provides "Deep Dive" info on a tracker, such as the SIM card number (ICCID), purchase date, and hardware model.
- **`fetch_mileage.py`**: Uses Protrack's mileage aggregation endpoint to calculate total distance traveled over a specific date range.

### **Active Testing**
- **`check_and_immobilize_device.py`**: Verifies that a device is currently online and responding before dispatching a relay command.
- **`analyze_immobilization_status.py`**: Checks if a device supports immobilization and reports its current ignition/cutoff state without modifying them.
- **`example_usage.py`**: Demonstrates the full integration flow for developers looking to import these scripts into the backend.

---

## 🛠 Usage Example

```bash
# 1. List all active trackers in the account
python list_devices.py

# 2. Inspect a specific tracker's hardware
python get_device_details.py <IMEI>

# 3. Test a security cutoff
python check_and_immobilize_device.py
```
