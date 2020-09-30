"""

broker-for-pubsub

Pub/Sub will keep trying until an HTTP route returns a 200.
This means that poorly-formed messages can ricochet through the system causing errors to be
over-represented. This function consumes 400 (Bad Request / validation failed json) and
 500 (server error) responses and notifies an admin, rather than retrying.


"""

import os


target_url = os.environ.get('TARGET_URL')


def request_to_pubsub(request):
    """
    Responds to a render request
    Args:
        request (flask.Request): HTTP request object with JSON payload.
    Returns:
        JSON message in response.
    """
    payload = request.get_json(force=True)