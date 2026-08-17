import logging
from pathlib import Path
from datetime import datetime


# ==========================================
# Root Log Directory
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_FOLDER = BASE_DIR / "logs"

LOG_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# Logger
# ==========================================

def get_logger():

    logger = logging.getLogger("retail_automation_logger")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # ------------------------------------------
    # Daily Log File
    # ------------------------------------------

    log_file = (
        LOG_FOLDER
        / f"retail_{datetime.now():%Y-%m-%d}.log"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # ------------------------------------------
    # File Handler
    # ------------------------------------------

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    # ------------------------------------------
    # Console Handler
    # ------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    # ------------------------------------------
    # Register Handlers
    # ------------------------------------------

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger