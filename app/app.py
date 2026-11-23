
import time

from flask import Flask, Response, g, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# I create the Flask web application.
app = Flask(__name__)

# I track the total number of HTTP requests.
REQUEST_COUNT = Counter(
    "demo_http_requests_total",
    "Total HTTP requests received by the application",
    ["method", "endpoint", "status"]
)

# I track the response duration of HTTP requests.
REQUEST_LATENCY = Histogram(
    "demo_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"]
)

# I record when each request starts.
@app.before_request
def start_timer():
    g.start_time = time.perf_counter()

# I record request metrics after the response is generated.
@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        duration = time.perf_counter() - g.start_time

        endpoint = request.path
        if endpoint not in ["/", "/health", "/error"]:
            endpoint = "/other"

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(response.status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=endpoint
        ).observe(duration)

    return response

# I create the home endpoint.
@app.route("/")
def home():
    return {
        "message": "Welcome to Prometheus AI Monitoring!",
        "application": "Python Flask Monitoring Demo"
    }

# I create an endpoint for Kubernetes health checks.
@app.route("/health")
def health():
    return {"status": "healthy"}

# I create a demo endpoint that returns HTTP 500.
@app.route("/error")
def error():
    return {"error": "Simulated application error"}, 500

# I expose metrics in Prometheus format.
@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )

# I start the application on port 5000.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
