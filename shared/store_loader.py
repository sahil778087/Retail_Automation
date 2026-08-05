import pandas as pd

from .config import STORE_FILE


def load_stores() -> pd.DataFrame:
    """
    Load and standardize the store master file.
    """

    df = pd.read_csv(STORE_FILE)

    df = df.rename(
        columns={
            "storeID": "store_id",
            "storeName": "store_name"
        }
    )

    required_columns = [
        "store_id",
        "store_name"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in stores.csv: {missing_columns}"
        )

    return df[required_columns]