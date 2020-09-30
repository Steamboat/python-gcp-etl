"""

Request-to-pubsub

Consume a request with a JSON payload.
Unpack the payload, inspect for a few values, and repack for a PUB/SUB topic.


Requirements:
google-cloud-pubsub

"""


import os
from werkzeug.exceptions import BadRequest
from etl.pubsub import request_to_pubsub


PROJECT_ID = os.environ.get('PROJECT_ID')
TOPIC_NAME = os.environ.get('TOPIC_NAME', 'backend-worker')


def validate_payload(payload):
    """
    Key / schema check to validate payload before Pub/Sub.
    Full validation is handled at the API, but this should filter out some basic noisy requests.
    """
    if 'message' not in payload.keys():
        raise BadRequest('user_id not in request payload json keys')
    if 'data' not in payload.keys():
        raise BadRequest('data not in request json keys')


def pubsub_forwarder(request):
    return request_to_pubsub(request, topic=TOPIC_NAME, validation_func=validate_payload)
