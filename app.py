
import logging
import os
from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    generate_latest,
    CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# Store application logs in a file and send them to the console
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log")
    ],
    force=True
)

logger = logging.getLogger(__name__)

# Count incoming HTTP requests
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of application requests",
    ["method", "endpoint", "status"]
)

@app.after_request
def record_request(response):
    REQUEST_COUNT.labels(
        request.method,
        request.endpoint or "unknown",
        str(response.status_code)
    ).inc()

    logger.info(
        "%s %s returned %s",
        request.method,
        request.path,
        response.status_code
    )

    return response

@app.route("/")
def home():
    return jsonify(message="CI/CD application is running!")

@app.route("/health")
def health():
    return jsonify(status="healthy"), 200

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
