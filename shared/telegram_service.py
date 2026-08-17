import requests

from shared.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


def send_telegram_message(message):
    """
    Send a message to the configured Telegram chat.
    """

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is not configured")

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"Telegram API error {response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram API error: {result}"
        )

    return result