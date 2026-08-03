import os
from dotenv import load_dotenv

load_dotenv()

# Authentication
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_URL = os.getenv("AUTH_URL")

# Inventory API
INVENTORY_URL = os.getenv("INVENTORY_URL")
CHAIN_ID = os.getenv("CHAIN_ID")
THIRD_PARTY_CHAIN_ID = os.getenv("THIRD_PARTY_CHAIN_ID")

# ==========================================
# API Configuration
# ==========================================

API_TIMEOUT = 60          # seconds
MAX_RETRIES = 3           # Future enhancement

# ==========================================
# CSV Configuration
# ==========================================

CSV_ENCODING = "utf-8-sig"
CSV_INDEX = False

# Paths
STORE_FILE = os.getenv("STORE_FILE")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
LOG_FILE = os.getenv("LOG_FILE")