
import os
import json
import base64
from flask import jsonify
from google.cloud import pubsub_v1


def publish_to_pubsub(topic, data, message=None, project_id=None):
    """
    Send a message with a data payload to pub/sub
    """
    project_id = project_id or os.environ.get('PROJECT_ID')
    publisher = pubsub_v1.PublisherClient()
    topic_name = f'projects/{project_id}/topics/{topic}'
    if message is not None:
        future = publisher.publish(topic_name, json.dumps(data).encode("utf-8"), message=message.encode("utf-8"))
    else:
        future = publisher.publish(topic_name, json.dumps(data).encode("utf-8"))
    result = str(future.result())
    print({"published_message_id", result})
    return result


def unpack_event(event):
    """
    Get the 'message' and 'data' from a pubsub event
    """
    data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    attributes = event['attributes']
    return data, attributes


def request_to_pubsub(request, topic=None, validation_func=None):
    """
    Responds to a request to publish
    Args:
        request (flask.Request): HTTP request object with JSON payload. Payload should have the following schema:
        {
            "message": "blah",  # Will be used to ID the message upstream source in pubsub
            "data": {}  # Will be passed as a JSON payload to the target Topic as an argument called data
        }
        topic: Pub/Sub topic to add the message to.
        validation_func: Function to validate a JSON payload and throw a BadRequest exception if it doesn't validate.
    Returns:
        JSON message in response.
    """
    payload = request.get_json(force=True)
    print({"payload", payload})
    topic = topic or payload.get('topic') or os.environ.get('TOPIC_NAME')
    if topic is None:
        raise EnvironmentError('topic must be specified in the parameters or request as "topic" '
                               'or environment as TOPIC_NAME')
    if validation_func is not None and callable(validation_func) is True:
        validation_func(payload=payload)
    result = publish_to_pubsub(topic=topic, message=f"request forwarded from {request.full_path}", data=payload)
    return jsonify({'message_id': result})
