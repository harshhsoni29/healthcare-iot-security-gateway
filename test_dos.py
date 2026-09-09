import time
import requests
import urllib3

# Disable SSL warnings for local self-signed certificate testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GATEWAY_URL = "https://127.0.0.1:5000/api/v1/telemetry"

def test_dos_mitigation():
    print("=== STRIDE SEC-TEST: Denial of Service (DoS) Mitigation ===")
    
    payload = {
        "device_id": "DEV-002",
        "vitals": {"heart_rate": 80, "spo2": 99, "blood_pressure": "118/75"}
    }
    headers = {"X-API-KEY": "secret_key_002", "Content-Type": "application/json"}

    print("[TEST] Launching rapid request burst (8 requests in 1 second)...")
    success_count = 0
    throttled_count = 0

    for i in range(8):
        res = requests.post(GATEWAY_URL, json=payload, headers=headers, verify=False)
        if res.status_code == 200:
            success_count += 1
            print(f" Request {i+1}: 200 OK")
        elif res.status_code == 429:
            throttled_count += 1
            print(f" Request {i+1}: 429 Too Many Requests (Throttled)")

    print(f"\n[RESULTS] Ingested: {success_count} | Throttled: {throttled_count}")
    assert throttled_count > 0, "Failed: DoS flood was not rate limited!"
    print(">>> SUCCESS: Rate limiter successfully mitigated traffic flood!\n")

if __name__ == "__main__":
    test_dos_mitigation()