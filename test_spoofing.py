import requests
import urllib3

# Disable SSL warnings for local self-signed certificate testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GATEWAY_URL = "https://127.0.0.1:5000/api/v1/telemetry"

def test_spoofing_mitigation():
    print("=== STRIDE SEC-TEST: Spoofing Mitigation ===")
    
    # 1. Valid Key Test
    valid_payload = {
        "device_id": "DEV-001",
        "vitals": {"heart_rate": 72, "spo2": 98, "blood_pressure": "120/80"}
    }
    valid_headers = {"X-API-KEY": "secret_key_001", "Content-Type": "application/json"}
    
    res_valid = requests.post(GATEWAY_URL, json=valid_payload, headers=valid_headers, verify=False)
    print(f"[TEST 1] Authorized Key Request -> Status: {res_valid.status_code} (Expected: 200)")
    assert res_valid.status_code == 200, "Failed: Valid key was rejected!"

    # 2. Invalid Key Test (Spoofed Device)
    spoofed_headers = {"X-API-KEY": "INVALID_FORGED_KEY", "Content-Type": "application/json"}
    res_spoof = requests.post(GATEWAY_URL, json=valid_payload, headers=spoofed_headers, verify=False)
    print(f"[TEST 2] Spoofed Key Request -> Status: {res_spoof.status_code} (Expected: 403)")
    assert res_spoof.status_code == 403, "Failed: Spoofed key was not blocked!"

    # 3. Elevation of Privilege Check (Admin Endpoint without Role)
    admin_url = "https://127.0.0.1:5000/admin/reset-limits"
    res_admin = requests.post(admin_url, headers={"X-User-Role": "UnauthorizedUser"}, verify=False)
    print(f"[TEST 3] Unauthorized Admin Access -> Status: {res_admin.status_code} (Expected: 403)")
    assert res_admin.status_code == 403, "Failed: Privilege escalation was allowed!"

    print(">>> SUCCESS: All Spoofing & Authorization tests passed!\n")

if __name__ == "__main__":
    test_spoofing_mitigation()