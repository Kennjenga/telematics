# Unified Telematics CLI Testing Plan

## Objective
Combine the standalone scripts from `protrack/` and `iopgps/` into a single, cohesive CLI tool located at the root of the `telematics/` directory. This acts as a "one-stop" interface to test any telematics provider integrated into Dere without needing to navigate into separate projects or deal with multiple `main.py` files.

## Proposed User Experience
Developers should activate a single virtual environment and use an intuitive terminal command to test interactions:

```bash
# Example 1: Authenticate and get device info
python cli.py --provider protrack --action info --device <IMEI>

# Example 2: Fire an immobilization command
python cli.py --provider protrack --action immobilize --device <IMEI>

# Example 3: Test IOPGPS telemetry processing
python cli.py --provider iopgps --action info --device <IMEI>
```

## Implementation Steps

1. **Centralize the Virtual Environment (Completed)**
   - Maintain only one `venv` at `/home/trino/dere/telematics/venv`.
   - Maintain a single `/telematics/.env` file containing all provider credentials.
   - Maintain a unified `/telematics/requirements.txt` (`requests`, `python-dotenv`, `argparse`).

2. **Refactor Provider Modules**
   - Convert `protrack/` and `iopgps/` directories into proper Python packages by adding `__init__.py` files.
   - Standardize their internal functions (e.g. `get_access_token`, `get_device_status`, `immobilize_device`) so they take the identical arguments: `(device_id: str)`.
   - Expose higher-level abstracted base classes for testing scripts.

3. **Build `cli.py` (The Unified Entrypoint)**
   - Use Python's built-in `argparse` to parse arguments.
   - Accept the `--provider` (`protrack` | `iopgps`) argument.
   - Dynamically load the correct sub-module based on the targeted provider.
   - Read the relevant fallback credentials automatically from `os.getenv` using `load_dotenv`.

4. **Expand Supported Actions**
   - `--action token`: Only grabs and outputs the auth token to ensure credentials are correct.
   - `--action status`: Resolves the status, ignition, mileage, and immobilization capabilities of a device.
   - `--action set-immobilize`: Triggers relay cutoff mapping exactly to how the Django backend would invoke it.
   - `--action set-restore`: Restores the relay mapping exactly to how the Django backend invokes it.

5. **Future Proofing**
   - As new telematics providers (like Wanway or Ruptela) are added to Dere, developers simply create a new folder `telematics/new-provider`, expose the standard functions, and add a single `--provider new-provider` mapping variable in `cli.py`.
