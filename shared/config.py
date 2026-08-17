import os

from dotenv import load_dotenv


load_dotenv()

# ==========================================
# Environment
# ==========================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "sandbox"
)

if ENVIRONMENT not in {"sandbox", "production"}:
    raise ValueError(
        f"Invalid ENVIRONMENT: {ENVIRONMENT}. "
        "Expected 'sandbox' or 'production'."
    )

# ==========================================
# Authentication
# ==========================================

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_URL = os.getenv("AUTH_URL")


# ==========================================
# Inventory API
# ==========================================

INVENTORY_URL = os.getenv("INVENTORY_URL")
CHAIN_ID = os.getenv("CHAIN_ID")
THIRD_PARTY_CHAIN_ID = os.getenv("THIRD_PARTY_CHAIN_ID")


# ==========================================
# Sales API
# ==========================================

SALES_API_URL = os.getenv("SALES_API_URL")


# ==========================================
# Master Data APIs
# ==========================================

CATEGORY_URL = os.getenv("CATEGORY_URL")
SUBCATEGORY_URL = os.getenv("SUBCATEGORY_URL")
BRAND_URL = os.getenv("BRAND_URL")
PRODUCT_URL = os.getenv("PRODUCT_URL")


# ==========================================
# API Configuration
# ==========================================

API_TIMEOUT = 60
MAX_RETRIES = 3


# ==========================================
# CSV Configuration
# ==========================================

CSV_ENCODING = "utf-8-sig"
CSV_INDEX = False


# ==========================================
# Paths
# ==========================================

STORE_FILE = os.getenv("STORE_FILE")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
LOG_FILE = os.getenv("LOG_FILE")


# ==========================================
# Database Configuration
# ==========================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ==========================================
# Telegram Notification Configuration
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# Configuration Validation
# ==========================================

def validate_config():
    """
    Validate required environment configuration.

    Raises
    -------
    ValueError
        If one or more required configuration
        values are missing.
    """

    required_config = {
        "CLIENT_ID": CLIENT_ID,
        "CLIENT_SECRET": CLIENT_SECRET,
        "AUTH_URL": AUTH_URL,

        "INVENTORY_URL": INVENTORY_URL,
        "CHAIN_ID": CHAIN_ID,
        "THIRD_PARTY_CHAIN_ID": THIRD_PARTY_CHAIN_ID,

        "SALES_API_URL": SALES_API_URL,

        "CATEGORY_URL": CATEGORY_URL,
        "SUBCATEGORY_URL": SUBCATEGORY_URL,
        "BRAND_URL": BRAND_URL,
        "PRODUCT_URL": PRODUCT_URL,

        "STORE_FILE": STORE_FILE,
        "OUTPUT_FILE": OUTPUT_FILE,

        "DB_HOST": DB_HOST,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,

        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    }

    missing = [
        name
        for name, value in required_config.items()
        if not value
    ]

    if missing:

        raise ValueError(
            "Missing required configuration: "
            + ", ".join(missing)
        )