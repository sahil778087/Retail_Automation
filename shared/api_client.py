import requests

from .config import API_TIMEOUT


def post(url, payload, headers):
    """
    Generic POST request helper.
    """

    response = requests.post(
        url=url,
        json=payload,
        headers=headers,
        timeout=API_TIMEOUT
    )

    response.raise_for_status()

    return response.json()