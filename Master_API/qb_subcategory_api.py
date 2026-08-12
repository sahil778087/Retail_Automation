from shared.api_client import post

from shared.config import SUBCATEGORY_URL


def fetch_sub_categories(token):

    headers = {
        "Content-Type": "application/ecmascript",
        "Authorization": token
    }

    payload = {
        "page": "1"
    }

    return post(
        SUBCATEGORY_URL,
        payload,
        headers
    )