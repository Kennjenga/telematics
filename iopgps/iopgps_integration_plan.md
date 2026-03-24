IOPGPS Integration Plan for Telematics
Summary
Integrate IOPGPS as a first-class provider by mirroring the Protrack pattern: implement a new provider client, register it, seed provider schema, and add provider-focused tests. Keep all existing telematics APIs/services unchanged by returning the normalized telemetry shape and standard exceptions.

Implementation Plan
Create IOPGPSClient in telematics/providers/iopgps.py.
Implement auth flow against https://api.itrack.top/api/authorization with signature md5(md5(password)+time), token cache in-instance only, and token refresh/retry on 10010/10011/10012.
Implement ABC methods from telematics/providers/base.py using existing exception types.
Implement get_device_list() even though it is not in the ABC, because views/serializers call it.
Register provider mapping "IOPGPS": IOPGPSClient in telematics/providers/registry.py.
Export IOPGPSClient in telematics/providers/__init__.py.
Add seed entry in management/commands/seed_telematics_providers.py with name="IOPGPS" and password.sensitive=True.
Add tests in telematics/tests/test_telematics_providers.py covering auth, retries, normalization, playback mileage, pagination, device-not-found, registry resolution, and unsupported immobilize/restore behavior.
Provider Behavior Spec (Decision-Complete)
__init__(account):
Read decrypted account_fields via base class.
Require account and password.
Set base_url = credentials.get("base_url", "https://api.itrack.top").
Keep _cached_token and _token_expires_at in memory only.
authenticate():
Call _get_access_token().
Return dict in same style as Protrack (token, authenticated, timestamp).
get_latest_telemetry(device_id):
Call /api/track?access_token=...&imeis=<device_id>.
Map first record to normalized keys exactly:
ignition, immobilize_status, speed, latitude, longitude, timestamp, mileage, today_mileage, direction, raw_data.
ignition: True when accstatus == 1, else False.
immobilize_status: True when oilpowerstatus == 0 (immobilized), else False.
timestamp: ISO 8601 from gpstime (fallback hearttime then servertime).
mileage: 0.0 when API has no odometer field.
today_mileage: computed from same-day /api/playback via Haversine sum (km), paginated until page size < 1000.
Keep raw_data untouched as provider payload record.
get_device_status(device_id):
Reuse track record and return normalized status dict with status in ACTIVE|DELAY|INACTIVE.
Status mapping default:
datastatus=2 -> ACTIVE, datastatus=4 -> DELAY, datastatus in (1,3) -> INACTIVE.
Include last_sync and optional battery/signal-like fields if present.
get_device_list():
Use /api/track with comma-separated IMEIs only when explicitly provided is not feasible; default strategy:
If provider lacks all-devices endpoint, raise ProviderAPIError with clear message and status 501.
If account-level default IMEI list is supplied in account_fields (optional extension), fetch and return normalized list from those IMEIs.
This preserves current app behavior while making capability explicit.
get_mileage(device_id):
Return Optional[float] per ABC contract.
Use same-day playback distance (km) as best available proxy.
Return None only if playback unavailable; otherwise float km.
get_mileage_report(device_ids, begintime, endtime):
For each IMEI, fetch /api/playback with pagination.
Parse record string (lon,lat,gpstime,speed,course;...).
Compute total km with Haversine.
Return Protrack-compatible structure:
{imei: [{"mileage": km, "begintime": begintime, "endtime": endtime, "raw_data": ...}]}.
immobilize(device_id) and restore(device_id):
Do not fake success.
Default behavior: raise ProviderAPIError("IOPGPS immobilize/restore is not supported by current public API.", http_status=501).
Error Mapping
20001 -> AuthenticationError.
10010/10011/10012 -> token refresh then retry once; if still failing AuthenticationError.
10013 and 20005 -> DeviceNotFoundError.
10009 -> RateLimitError (retry_after when available).
10014 -> AuthenticationError (clock skew/request time).
Any other non-zero code -> ProviderAPIError with mapped message and carried error_code/http_status.
API / Type Impacts
No REST endpoint contract changes.
No DB schema/migration changes.
New provider name contract: DB TelematicsProvider.name == "IOPGPS" must exactly match registry key.
TelematicsProviderAccount.account_fields schema extended by seed command for IOPGPS credentials.
Test Cases
Registry factory resolves "IOPGPS" to IOPGPSClient; unknown provider raises ValueError.
Authentication success returns token.
Authentication failure (20001) raises AuthenticationError.
Token expiry (10012) triggers refresh + retry path.
Telemetry normalization returns all 10 required keys and expected types.
Playback distance conversion validates expected km from known points.
Device not found (20005) raises DeviceNotFoundError.
get_device_list() capability behavior is explicit and deterministic.
immobilize/restore raise unsupported error with clear message.
Mileage report pagination combines 1000+N playback records correctly.
Assumptions and Defaults
We will follow the existing ABC signatures from base.py even where your draft snippet differs.
Unsupported immobilize/restore is safer than geofence side-effects; default is explicit 501 error.
When IOPGPS does not expose true odometer, mileage is set to 0.0 and today_mileage is computed from playback.
No extra Vehicle linkage checks will be added in provider methods; callers already enforce provider_account + device_id.
