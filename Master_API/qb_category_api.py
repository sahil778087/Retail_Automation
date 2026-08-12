from shared.api_client import post

from shared.config import CATEGORY_URL


def fetch_categories(token):

    headers = {
        "Content-Type": "application/ecmascript",
        "Authorization": token
    }

    payload = {
        "page": "1"
    }

    return post(
        CATEGORY_URL,
        payload,
        headers
    )