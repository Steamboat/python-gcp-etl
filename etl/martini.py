"""

martini (deprecated)

Hit me. Hit me. I bet a dime. Hit me.

Poke a service and log its response time. Deprecated in favor of GCP Uptime Monitoring.

This should be called from Cloud Scheduler or Airflow or some other orchestration service as part of a
quality-assurance / heartbeat / keepalive system.

Invoke with JSON payload:
{
    "target_url": "http",
    "data": {}  # Will be passed as a JSON payload to the target URL
}

Data is logged with python-json-logger, which packages the data into a neat little json log entry
that is easy to parse through.

Requirements:
python-json-logger
requests

"""

import time
import logging
import requests
from flask import jsonify
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


def martini(request):
    """
    Responds to a render request
    Args:
        request (flask.Request): HTTP request object with JSON payload. JSON should follow this schema:
        {
            "target_url": "http",
            "data": {}  # Will be passed as a JSON payload to the target URL
        }
    Returns:
        JSON message in response.
    """
    payload = request.get_json(force=True)
    target_url = payload['target_url']
    start_time = time.time()
    # Post JSON to the route if specified else use a GET request
    data = payload.get('data')
    if data is not None:
        response = requests.post(target_url, json=data)
    else:
        response = requests.get(target_url)
    end_time = time.time()
    data = {"target_url": target_url,
            "response_time": end_time - start_time,
            "response_time_ms": (end_time - start_time) * 1000,
            "status_code": response.status_code}
    logger.debug("hit me.", extra=data)
    return jsonify(data)
