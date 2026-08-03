from .api_client import post    # . here means from the same package

from .config import (
    AUTH_URL,
    CLIENT_ID,
    CLIENT_SECRET
)


def get_partner_token():

    payload = {
        "clientID": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }

    headers = {
        "Content-Type": "application/json"
    }

    data = post(
        AUTH_URL,
        payload,
        headers
    )

    if not data.get("status"):
        raise Exception("Partner Token Generation Failed")

    return {
        "token": data["token"],
        "issued_at": data["issued_at"],
        "expires": data["expires"]
    }