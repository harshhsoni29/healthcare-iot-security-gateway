import time
import random
import json
import os
import requests

# Disable SSL warnings for self-signed development certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GATEWAY_URL = "https://127.0.0.1:5000/api/v1/telemetry"
CACHE_FILE = "offline_cache.json"

# Dynamically generate credentials matching all 50 registered devices
DEVICES = {
    f"DEV-{i:03d}": f"secret_key_{i:03d}" for i in range(1, 51)
}


def cache_failed_telemetry(payload):
    """Fallback offline caching: Preserves data locally when gateway is unreachable or throttling."""
    cache = []
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            cache = []

    cache.append(payload)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)
    print(f"[OFFLINE CACHE] Telemetry stored locally. Total cached items: {len(cache)}")


def flush_offline_cache():
    """Flushes cached offline telemetry back to the gateway when connection stabilizes."""
    if not os.path.exists(CACHE_FILE):
        return

    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    except json.JSONDecodeError:
        return

    if not cache:
        return

    print(f"[OFFLINE CACHE] Attempting to flush {len(cache)} cached items to gateway...")
    remaining_cache = []

    for item in cache:
        device_id = item.get("device_id")
        api_key = DEVICES.get(device_id, "")
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

        try:
            response = requests.post(GATEWAY_URL, json=item, headers=headers, verify=False, timeout=2)
            if response.status_code == 200:
                print(f"[OFFLINE CACHE FLUSH SUCCESS] Ingested cached payload for {device_id}")
            else:
                remaining_cache.append(item)
        except requests.exceptions.RequestException:
            remaining_cache.append(item)

    with open(CACHE_FILE, "w") as f:
        json.dump(remaining_cache, f, indent=4)


def generate_vitals(device_id):
    """Generates synthetic medical telemetry for 50 simulated clinical streams."""
    return {
        "device_id": device_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vitals": {
            "heart_rate": random.randint(60, 100),
            "spo2": random.randint(95, 100),
            "blood_pressure": f"{random.randint(110, 130)}/{random.randint(70, 85)}"
        }
    }


def run_simulator():
    """Main simulation loop emitting secure telemetry across 50 devices over HTTPS."""
    print("[SIMULATOR START] Initiating 50-device vital sign transmission loop...")
    
    while True:
        # Check and flush any previously cached payloads
        flush_offline_cache()

        # Iterate over all 50 devices
        for device_id, api_key in DEVICES.items():
            payload = generate_vitals(device_id)
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }

            try:
                # Transmit over SSL (verify=False handles local self-signed certs)
                response = requests.post(GATEWAY_URL, json=payload, headers=headers, verify=False, timeout=3)
                
                if response.status_code == 200:
                    print(f"[TRANSMISSION SUCCESS] {device_id} -> Gateway (200 OK)")
                elif response.status_code == 429:
                    print(f"[THROTTLED] {device_id} rate limited (429). Storing in offline cache.")
                    cache_failed_telemetry(payload)
                else:
                    print(f"[REJECTED] {device_id} failed with status {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"[GATEWAY UNREACHABLE] Connection error for {device_id}. Caching telemetry locally.")
                cache_failed_telemetry(payload)

            time.sleep(0.2)  # Short delay between device transmissions


if __name__ == "__main__":
    run_simulator()