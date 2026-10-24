# CloudPulse - production-style Flask app for Kubernetes on Google Cloud
import os
import socket
import time
import platform
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request, g
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# App settings come from environment variables (12-factor style, set via K8s ConfigMap later)
APP_NAME = os.getenv("APP_NAME", "CloudPulse")
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
APP_ENV = os.getenv("APP_ENV", "dev")
START_TIME = time.time()

# Prometheus metrics: request count and latency per endpoint
REQUEST_COUNT = Counter(
    "cloudpulse_requests_total", "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "cloudpulse_request_latency_seconds", "Request latency in seconds",
    ["endpoint"],
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)


def get_info():
    # Collect runtime details shown on the dashboard
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "hostname": socket.gethostname(),          # Pod name when running on Kubernetes
        "pod_ip": os.getenv("POD_IP", "local"),    # Injected by K8s Downward API later
        "python": platform.python_version(),
        "uptime_seconds": int(time.time() - START_TIME),
        "server_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


@app.before_request
def start_timer():
    # Save request start time to measure latency
    g.start_time = time.time()


@app.after_request
def record_metrics(response):
    # Use the route pattern (not raw path) to keep metric labels low-cardinality
    endpoint = request.url_rule.rule if request.url_rule else "unknown"
    if endpoint != "/metrics":
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint).observe(time.time() - g.start_time)
    return response


@app.route("/")
def dashboard():
    # Render the visual dashboard page
    return render_template("index.html", info=get_info())


@app.route("/api/info")
def api_info():
    # JSON API used by the dashboard for live updates
    return jsonify(get_info())


@app.route("/health")
def health():
    # Liveness probe: is the process alive?
    return jsonify(status="healthy"), 200


@app.route("/ready")
def ready():
    # Readiness probe: is the app ready to receive traffic?
    return jsonify(status="ready"), 200


@app.route("/metrics")
def metrics():
    # Prometheus scrape endpoint
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    # Listen on all interfaces so it works inside a container
    app.run(host="0.0.0.0", port=8080)
