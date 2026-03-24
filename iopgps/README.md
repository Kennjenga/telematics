# IOPGPS Standalone Testing Module

This module provides standalone scripts for interacting with the IOPGPS Open API via `https://open.iopgps.com`.

## 🚀 API Endpoint Reference

| Command / File | Endpoint | Method | Key Headers/Params | Response Highlights |
| :--- | :--- | :---: | :--- | :--- |
| **`main.py`** | `/api/auth` | `POST` | `appid`, `signature` | `accessToken`, `expiresIn` |
| **`list_devices.py`** | `/api/device` | `GET` | `accessToken`, `pageSize` | `data` (list of devices), `code` |
| **`get_device_details.py`** | `/api/device/detail` | `GET` | `imei`, `accessToken` | `deviceBrief`, `account`, `vehicleBean` |
| **`fetch_mileage.py`** | `/api/device/miles` | `GET` | `imei`, `startTime`, `endTime`, `accessToken` | `miles`, `runTime` |
| **`device_commands.py`** | `/api/device/status` | `GET` | `imei`, `accessToken` | `acc` (Ignition), `oil` (Relay status) |
| **`check_and_immobilize_device.py`**| `/api/instruction/relay` | `POST` | `parameter`: "2" (Cut), `imeis`, `accessToken` | `code`, `result`, `uuid` |

---

## 📂 File Explanations

### **Core Logic**
- **`main.py`**: The authentication entry point. It handles the `md5(md5(secret) + time)` signature generation and retrieves the `accessToken` used by all other scripts.
- **`device_commands.py`**: A library containing the low-level functions for checking status and sending relay commands. It maps raw IOPGPS codes (like `parameter: 2` for immobilization) into readable results.

### **Discovery & Data**
- **`list_devices.py`**: Primarily used to verify which IMEIs are assigned to the `testdemo` account. It displays a count and a summary of every device found.
- **`get_device_details.py`**: Fetches the complete technical datasheet for a specific device, including its hardware type (`deviceType`), account owner, and vehicle binding info (`vin`).
- **`fetch_mileage.py`**: Contains the logic to query distance statistics (`miles`) for a specific time window.

### **Active Testing**
- **`check_and_immobilize_device.py`**: Our primary test runner for immobilization. It gets a token, verifies the current status of the tracker, and attempts to send the relay cutoff instruction.
- **`analyze_immobilization_status.py`**: A non-intrusive version of the check script that only reports current status without sending any commands.
- **`example_usage.py`**: A sample implementation showing how to chain the mileage scripts together to generate a `json` report.

---

## 🛠 Usage Example

```bash
# 1. Start by finding a valid IMEI
python list_devices.py

# 2. Get full details for that IMEI
python get_device_details.py <IMEI>

# 3. Test a command (Immobilize)
python check_and_immobilize_device.py
```
