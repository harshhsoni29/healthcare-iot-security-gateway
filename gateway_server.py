import time
from collections import defaultdict
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Dynamically generate 50 registered medical devices and API keys (DEV-001 to DEV-050)
REGISTERED_DEVICES = {
    f"DEV-{i:03d}": f"secret_key_{i:03d}" for i in range(1, 51)
}

# Rate Limiting Configuration (DoS Protection)
RATE_LIMIT_WINDOW = 10  # Time window in seconds
MAX_REQUESTS_PER_WINDOW = 5  # Max allowed requests per window
request_history = defaultdict(list)

# In-memory store for clinical dashboard visualization
dashboard_data = []


def is_rate_limited(device_id):
    """Sliding-window rate limiter to prevent DoS bursts."""
    current_time = time.time()
    timestamps = request_history[device_id]
    
    # Remove timestamps older than the sliding window
    request_history[device_id] = [t for t in timestamps if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[device_id]) >= MAX_REQUESTS_PER_WINDOW:
        return True
    
    request_history[device_id].append(current_time)
    return False


@app.route("/api/v1/telemetry", methods=["POST"])
def ingest_telemetry():
    """Ingresses patient telemetry with Spoofing and DoS mitigations."""
    api_key = request.headers.get("X-API-KEY")
    data = request.get_json()

    if not data or "device_id" not in data:
        return jsonify({"error": "Malformed payload"}), 400

    device_id = data["device_id"]

    # 1. Spoofing Verification
    if REGISTERED_DEVICES.get(device_id) != api_key:
        print(f"[SECURITY ALERT] Spoofing attempt detected for device: {device_id}")
        return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 403

    # 2. Denial of Service (Rate Limit) Verification
    if is_rate_limited(device_id):
        print(f"[SECURITY ALERT] Rate limit exceeded for device: {device_id}")
        return jsonify({"error": "Too Many Requests: Traffic burst throttled"}), 429

    # Successful ingestion & dashboard logging
    print(f"[GATEWAY SECURE RECEIVE] Telemetry logged for {device_id}: {data}")
    dashboard_data.append(data)
    
    return jsonify({
        "status": "success",
        "message": "Telemetry securely ingested",
        "timestamp": time.time()
    }), 200


@app.route("/admin/reset-limits", methods=["POST"])
def reset_limits():
    """Elevation of Privilege mitigation: Protects admin controls via role checking."""
    user_role = request.headers.get("X-User-Role")
    
    if user_role != "Admin":
        print("[SECURITY ALERT] Elevation of Privilege attempt blocked on admin endpoint.")
        return jsonify({"error": "Forbidden: Admin role required for privilege escalation"}), 403

    request_history.clear()
    return jsonify({"status": "success", "message": "Rate limits reset by Administrator"}), 200


@app.route("/dashboard", methods=["GET"])
def clinical_dashboard():
    """Lightweight clinical interface rendering real-time telemetry feed."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clinical Telemetry Dashboard</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f7f6; }
            h2 { color: #2c3e50; }
            table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #007bff; color: white; }
            tr:hover { background-color: #f1f1f1; }
        </style>
    </head>
    <body>
        <h2>Live Patient Telemetry Feed (STRIDE Secured - 50 Active Devices)</h2>
        <table>
            <tr>
                <th>Device ID</th>
                <th>Heart Rate (BPM)</th>
                <th>SpO2 (%)</th>
                <th>Blood Pressure</th>
                <th>Timestamp</th>
            </tr>
            {% for entry in data|reverse %}
            <tr>
                <td><strong>{{ entry.device_id }}</strong></td>
                <td>{{ entry.vitals.heart_rate }}</td>
                <td>{{ entry.vitals.spo2 }}%</td>
                <td>{{ entry.vitals.blood_pressure }}</td>
                <td>{{ entry.timestamp }}</td>
            </tr>
            {% else %}
            <tr><td colspan="5">No telemetry ingested yet.</td></tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, data=dashboard_data[-15:])


if __name__ == "__main__":
    # Information Disclosure Mitigation: Serves API over encrypted TLS transport (adhoc HTTPS)
    print("[STARTING GATEWAY] Launching HTTPS Secure Edge Gateway on port 5000 (50 Devices Configured)...")
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc", debug=True)