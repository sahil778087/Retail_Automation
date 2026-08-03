from shared.api_client import post

from shared.config import (
    INVENTORY_URL,
    CHAIN_ID,
    THIRD_PARTY_CHAIN_ID
)


def fetch_store_inventory(store_id, token):

    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    payload = {
        "thirdPartyChainID": THIRD_PARTY_CHAIN_ID,
        "chainID": CHAIN_ID,
        "storeID": store_id
    }

    return post(
        INVENTORY_URL,
        payload,
        headers
    )