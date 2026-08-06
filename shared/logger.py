import logging
from pathlib import Path
from datetime import datetime


LOG_FOLDER = Path("Inventory_API/logs")
LOG_FOLDER.mkdir(parents=True, exist_ok=True)


def get_logger():

    logger = logging.getLogger("inventory_logger")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    log_file = LOG_FOLDER / f"inventory_{datetime.now():%Y-%m-%d}.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger