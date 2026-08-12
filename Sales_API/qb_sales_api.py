import requests

from shared.config import (
    SALES_API_URL,
    CHAIN_ID,
    THIRD_PARTY_CHAIN_ID
)


def fetch_sales(
    sales_date: str,
    token: str
) -> dict:
    """
    Fetch sales transactions for a single date.

    Parameters
    ----------
    sales_date : str
        Date in YYYY-MM-DD format.

    token : str
        Partner authentication token.

    Returns
    -------
    dict
        Raw QueueBuster API response.
    """

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "third_party_chain_id": int(THIRD_PARTY_CHAIN_ID),
        "chain_id": int(CHAIN_ID),
        "sales_date": sales_date
    }

    response = requests.post(
        url=SALES_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("status"):
        raise Exception(
            data.get("message", "QueueBuster Sales API failed.")
        )

    return data