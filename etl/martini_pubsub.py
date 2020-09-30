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
import base64
from flask import jsonify
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


def martini(event, context):
    """
    Responds to a render request
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    message = base64.b64decode(event['data']).decode('utf-8')
    payload = event['attributes']
    target_url = payload['target_url']
    start_time = time.time()
    # Post JSON to the route if specified else use a GET request
    data = payload.get('data')
    if data is not None:
        response = requests.post(target_url, json=data)
    else:
        response = requests.get(target_url)
    end_time = time.time()
    data = {"message": message,
            "pub_message_id": context.event_id,
            "pub_timestamp": context.timestamp,
            "target_url": target_url,
            "response_time": end_time - start_time,
            "response_time_ms": (end_time - start_time) * 1000,
            "status_code": response.status_code}
    logger.debug("hit me.", extra=data)
    return jsonify(data)
