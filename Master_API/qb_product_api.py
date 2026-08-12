from shared.api_client import post

from shared.config import PRODUCT_URL


def fetch_products(token):

    headers = {
        "Content-Type": "application/ecmascript",
        "Authorization": token
    }

    payload = {
        "page": ""
    }

    return post(
        PRODUCT_URL,
        payload,
        headers
    )