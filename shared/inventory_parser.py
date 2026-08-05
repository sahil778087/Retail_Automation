import pandas as pd

# ==========================================
# QueueBuster → Canonical DataFrame Mapping
# ==========================================

COLUMN_MAPPING = {
    "productID": "product_id",
    "productName": "product_name",
    "unit": "unit",
    "categoryID": "category_id",
    "categoryName": "category_name",
    "subCategoryID": "sub_category_id",
    "subCategoryName": "sub_category_name",
    "brandID": "brand_id",
    "brandName": "brand_name",
    "barcode": "barcode",
    "inventoryLevel": "stock_quantity",
}

# Canonical column order
FINAL_COLUMNS = [
    "product_id",
    "product_name",
    "unit",
    "category_id",
    "category_name",
    "sub_category_id",
    "sub_category_name",
    "brand_id",
    "brand_name",
    "barcode",
    "store_id",
    "store_name",
    "stock_quantity",
]


def parse_inventory(
    response: dict,
    store_id: int,
    store_name: str
) -> pd.DataFrame:
    """
    Converts QueueBuster Inventory API response
    into the project's canonical inventory DataFrame.
    """

    # ----------------------------------------
    # Validate Response
    # ----------------------------------------

    if not response.get("status", False):
        raise ValueError(
            "QueueBuster API returned an unsuccessful response."
        )

    # ----------------------------------------
    # Extract catalogueData
    # ----------------------------------------

    catalogue = response.get("catalogueData", [])

    if not catalogue:
        return pd.DataFrame(columns=FINAL_COLUMNS)

    # ----------------------------------------
    # Create DataFrame
    # ----------------------------------------

    df = pd.DataFrame(catalogue)

    # ----------------------------------------
    # Keep Required Columns
    # ----------------------------------------

    df = df[list(COLUMN_MAPPING.keys())]

    # ----------------------------------------
    # Rename Columns
    # ----------------------------------------

    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # ----------------------------------------
    # Add Store Details
    # ----------------------------------------

    df["store_id"] = store_id
    df["store_name"] = store_name

    # ----------------------------------------
    # Reorder Columns
    # ----------------------------------------

    df = df[FINAL_COLUMNS]

    return df