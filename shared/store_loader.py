import pandas as pd

from .config import STORE_FILE


def load_stores() -> pd.DataFrame:
    """
    Load the store master file.

    Returns
    -------
    pd.DataFrame
        Columns:
        - StoreID
        - StoreName
    """

    return pd.read_csv(STORE_FILE)