# Dere Telematics Integrations

This repository contains standalone, backend-agnostic testing and exploration scripts for the telematics providers integrated into the Dere backend. 

Currently supported providers:
1. **Protrack** (`protrack/`)
2. **IOPGPS** (`iopgps/`)

These folders do not depend on Django or the application database. They exist exclusively for debugging API behaviors, testing raw telemetry endpoints, testing immobilize commands, and generating mileage logs directly against the provider endpoints.

## Single Master Setup

Instead of managing multiple virtual environments, this repository uses **one unified testing environment** at the root of the `telematics/` folder.

```bash
# 1. Navigate to the telematics root
cd /home/trino/dere/telematics

# 2. Create the master virtual environment
python3 -m venv venv

# 3. Activate the environment
source venv/bin/activate

# 4. Install dependencies globally for all scripts
pip install -r requirements.txt
```

## Environment Variables (.env)
We use a centralized `.env` file to ensure no sensitive credentials (like provider passwords, appids, or tokens) are tracked in git. 

Create a `.env` file in the root of the `telematics/` directory by copying the example:

```bash
cp .env.example .env
```

Fill in the appropriate credentials inside `.env` depending on the provider you are testing. Both `protrack/` and `iopgps/` scripts will automatically detect and pull from this root `.env` file.

## Protrack Scripts (`protrack/`)
The `protrack` folder comes with several utilities interacting with `api.protrack365.com`:

- **`main.py`**: Handles API authentication, signature generation (`md5(md5(password)+time)`), and extracts JWT/Access Tokens.
- **`analyze_immobilization_status.py`**: Queries device info (ignition, status, last sync, immobilize flag) and maps Protrack's raw values strings to readable formats.
- **`check_and_immobilize_device.py`**: An active test that checks the state and then dispatches the `Relay,1#` command to immobilize.
- **`example_usage.py`** & **`fetch_mileage.py`**: Batch requests and parses the total mileage by date window to a local JSON file. 

## IOPGPS Scripts (`iopgps/`)
The `iopgps` folder contains fully abstract tools communicating with `https://open.iopgps.com`. To keep maintenance extremely simple, these files identically mirror the structure found in the `protrack/` folder.

- **`main.py`**: Handles API authentication and signature generation using `appid` and `time` via `POST /api/auth`, keeping tokens local.
- **`analyze_immobilization_status.py`**: Queries device info mapping to Dere's `TelematicsProviderClient` specs by using `GET /api/device/status`.
- **`device_commands.py`**: Exposes the low-level `get_device_status` and triggers the `POST /api/instruction/relay` immobilize sequence mapping to parameter `"2"` for cutoff or `"1"` for restore.
- **`check_and_immobilize_device.py`**: End-to-end active test hitting the API directly to evaluate security cutoffs.
- **`example_usage.py`** & **`fetch_mileage.py`**: Batch requests leveraging the specific `GET /api/device/miles` endpoint for fetching cumulative km based on date limits.

## Future Plans (Unified CLI)
Be sure to read **`plan.md`** for the upcoming architecture roadmap! We are planning to merge all scripts from `protrack/` and `iopgps/` under a single universal `cli.py` root script to allow one-line testing like:
`python cli.py --provider iopgps --action status --device <IMEI>`
