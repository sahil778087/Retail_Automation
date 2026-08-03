import pandas as pd

from .config import (
    OUTPUT_FILE,
    CSV_ENCODING,
    CSV_INDEX
)


def export_inventory(df: pd.DataFrame):
    """
    Export inventory DataFrame to CSV.
    """

    df.to_csv(
        OUTPUT_FILE,
        index=CSV_INDEX,
        encoding=CSV_ENCODING
    )

    print("\n========================================")
    print("CSV Export Successful")
    print("========================================")

    print(f"Rows Exported : {len(df):,}")
    print(f"Location      : {OUTPUT_FILE}")