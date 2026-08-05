import pandas as pd

from .config import (
    OUTPUT_FILE,
    CSV_ENCODING,
    CSV_INDEX
)


def export_inventory(df: pd.DataFrame):
    """
    Export inventory DataFrame in the legacy format
    expected by the existing Power BI dashboard.
    """

    export_df = df[
        [
            "product_id",
            "product_name",
            "unit",
            "category_name",
            "sub_category_name",
            "store_id",
            "store_name",
            "stock_quantity",
        ]
    ].rename(
        columns={
            "product_id": "productID",
            "product_name": "Product Name",
            "unit": "Unit",
            "category_name": "Category",
            "sub_category_name": "SubCategory",
            "store_id": "StoreID",
            "store_name": "Store Name",
            "stock_quantity": "Stock",
        }
    )

    export_df.to_csv(
        OUTPUT_FILE,
        index=CSV_INDEX,
        encoding=CSV_ENCODING
    )

    print("\n========================================")
    print("CSV Export Successful")
    print("========================================")

    print(f"Rows Exported : {len(export_df):,}")
    print(f"Location      : {OUTPUT_FILE}")