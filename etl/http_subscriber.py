"""

http_subscriber

Pub/Sub will keep trying until an HTTP route returns a 200.
This means that poorly-formed messages can ricochet through the system causing errors to be
over-represented. This function consumes 400 (Bad Request / validation failed json) and
 500 (server error) responses and notifies an admin, rather than retrying. Erroneous messages
are dropped in a dead-letter queue for a later pull request.

Invoke with JSON payload:
{
    "target_url": "http",
    "data": {}  # Will be passed as a JSON payload to the target URL
}

Data is logged with python-json-logger, which packages the data into a neat little json log entry
that is easy to parse through.

Requirements:
python-json-logger
google-cloud-pubsub

"""

import os
import json
import logging
import base64
from flask import jsonify
from pythonjsonlogger import jsonlogger
from etl.http_tools import http_request
from etl.pubsub import publish_to_pubsub


logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


# Load environment variables
DEAD_LETTER_TOPIC = os.environ.get('DEAD_LETTER_TOPIC')
PROJECT_ID = os.environ.get('PROJECT_ID')
if any([var is None for var in (DEAD_LETTER_TOPIC, PROJECT_ID)]):
    raise EnvironmentError('The following env vars must be specified: DEAD_LETTER_TOPIC, PROJECT_ID')


def unpack_event(event):
    """
    Get the 'message' and 'data' from a pubsub event
    """
    data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    attributes = event['attributes']
    return data, attributes


def http_subscriber(event, context):
    """
    Turn a message from pub/sub into a request for the target URL.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    message = base64.b64decode(event['data']).decode('utf-8')
    attributes = event['attributes']
    target_url = attributes['target_url']
    payload = attributes.get('payload')
    response, data = http_request(target_url=target_url, payload=payload)
    data.update({"message": message, "pub_message_id": context.event_id, "pub_timestamp": context.timestamp})
    if response.status_code in (400, 500):
        logger.warning("http_subscriber", extra=data)
        publish_to_pubsub(topic=DEAD_LETTER_TOPIC, message=f'request failed for target_url={target_url}', data=data)
        return jsonify(data), 200
    else:
        logger.debug("http_subscriber", extra=data)
        return jsonify(data), response.status_code
