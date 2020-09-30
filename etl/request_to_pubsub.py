"""

Request-to-pubsub

Consume a request with a JSON payload.
Unpack the payload, inspect for a few values, and repack for a PUB/SUB topic.


Requirements:
google-cloud-pubsub

"""


import os
import json
from flask import jsonify
from google.cloud import pubsub_v1
from werkzeug.exceptions import BadRequest


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


def publish_to_pubsub(message, data):
    """
    Send a message with a data payload to pub/sub
    """
    publisher = pubsub_v1.PublisherClient()
    topic_name = f'projects/{PROJECT_ID}/topics/{TOPIC_NAME}'
    future = publisher.publish(topic_name, message.encode("utf-8"), data=json.dumps(data).encode("utf-8"))
    result = str(future.result())
    print({"published_message_id", result})
    return result


def request_to_pubsub(request):
    """
    Responds to a request to publish
    Args:
        request (flask.Request): HTTP request object with JSON payload. Payload should have the following schema:
        {
            "message": "blah",  # Will be used to ID the message upstream source in pubsub
            "data": {}  # Will be passed as a JSON payload to the target Topic as an argument called data
        }
    Returns:
        JSON message in response.
    """
    payload = request.get_json(force=True)
    print({"payload", payload})
    validate_payload(payload=payload)
    result = publish_to_pubsub(message=payload.get('message', 'worker-api-dev test message'),
                               data=payload.get('data', {}))
    return jsonify({'message_id': result})
