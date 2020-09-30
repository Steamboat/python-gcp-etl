
import time
import requests


def http_request(target_url, payload=None):
    """
    Send an HTTP request and collect some data about it.
    :param target_url: URL to target with the GET/POST request.
    :param payload: (optional) JSON payload to be passed to the endpoint with POST if applicable.
    Otherwise a GET request will be triggered.
    :return: Tuple of response, data - The full requests.response and the diagnostic data collected about it.
    """
    start_time = time.time()
    # Post JSON to the route if specified else use a GET request
    if payload is not None:
        response = requests.post(target_url, json=payload)
    else:
        response = requests.get(target_url)
    end_time = time.time()
    data = {"target_url": target_url,
            "response_time": end_time - start_time,
            "response_time_ms": (end_time - start_time) * 1000,
            "status_code": response.status_code}
    return response, data