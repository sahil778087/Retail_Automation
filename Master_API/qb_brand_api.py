from shared.api_client import post

from shared.config import BRAND_URL


def fetch_brands(token):

    headers = {
        "Content-Type": "application/ecmascript",
        "Authorization": token
    }

    payload = {
        "page": "1"
    }

    return post(
        BRAND_URL,
        payload,
        headers
    )