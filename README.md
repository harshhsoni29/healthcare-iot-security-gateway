# Healthcare IoT Threat Model & Secure Edge Gateway

A security-hardened Python/Flask edge gateway designed to securely ingest real-time medical device telemetry across 50 simulated clinical monitors over encrypted transport (`TLS/HTTPS`). The system incorporates systematic **STRIDE** threat model mitigations, automated attack testing, offline fallback caching, and a live clinical dashboard interface.

---

## Architecture Overview

[ 50 Medical Devices ] ---> ( X-API-KEY / TLS ) ---> [ Flask Edge Gateway ] ---> [ Live Clinical Dashboard ]
( DEV-001 - DEV-050 )                                       |
( Rate Limit / RBAC )
|
[ Local Cache Fallback ]

* **Ingestion Layer:** Accepts patient vital signs (`heart_rate`, `spo2`, `blood_pressure`) from registered devices (`DEV-001` through `DEV-050`).
* **Resilience Layer:** Implements local file fallback (`offline_cache.json`) to store payloads when network connectivity drops or rate limits trigger.
* **Visualization Layer:** Embedded clinical dashboard at `/dashboard` rendering live telemetry streams with auto-refresh capability.

---

## STRIDE Threat Model & Mitigations

| STRIDE Threat Category | Identified Risk | Engineering Mitigation | Verification Script |
| :--- | :--- | :--- | :--- |
| **Spoofing (S)** | Unauthenticated devices emitting false patient vitals | Machine-to-Machine `X-API-KEY` token verification on ingestion (`403 Forbidden` on mismatch) | `test_spoofing.py` |
| **Tampering (T)** | In-transit payload modification | Mandatory `TLS/HTTPS` encrypted transport using `ssl_context="adhoc"` | Verified via HTTPS handshake |
| **Information Disclosure (I)** | Unencrypted eavesdropping on medical telemetry | Enforcement of TLS transport layer encryption across all routes | Transport layer inspection |
| **Denial of Service (D)** | Traffic floods / rogue device bursts exhausting server capacity | In-memory sliding-window rate limiter (5 requests / 10s per device; `429 Too Many Requests`) | `test_dos.py` |
| **Elevation of Privilege (E)** | Non-admin actors triggering operational resets | Role-Based Access Control (RBAC) inspecting `X-User-Role` headers (`403 Forbidden` non-admin) | `test_spoofing.py` |

---

## Getting Started

### Prerequisites
* Python 3.8+
* Install required dependencies:
  ```powershell
  pip install -r requirements.txt

  Running the System
Launch the Secure Edge Gateway:

PowerShell
python gateway_server.py
Runs an HTTPS Flask server listening on https://127.0.0.1:5000.

Launch the 50-Device IoT Simulator:
Open a second terminal window and run:

PowerShell
python iot_simulator.py
Streams synthetic medical vitals from DEV-001 through DEV-050 over TLS.

View the Live Dashboard:
Open your browser and navigate to:

Plaintext
[https://127.0.0.1:5000/dashboard]

Automated Security Testing
Open a third terminal while the server and simulator are active to validate STRIDE mitigations under concurrent load:

PowerShell
# Test Spoofing (S) and Privilege Escalation (E)
python test_spoofing.py

# Test Denial of Service (D) Rate Limiting
python test_dos.py