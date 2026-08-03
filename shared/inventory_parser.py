import pandas as pd

# ==========================================
# QueueBuster → Power BI Column Mapping
# ==========================================

COLUMN_MAPPING = {
    "productID": "productID",
    "productName": "Product Name",
    "unit": "Unit",
    "categoryName": "Category",
    "subCategoryName": "SubCategory",
    "inventoryLevel": "Stock"
}

# Final column order expected by Power BI
FINAL_COLUMNS = [
    "productID",
    "Product Name",
    "Unit",
    "Category",
    "SubCategory",
    "StoreID",
    "Store Name",
    "Stock"
]


# ==========================================
# Inventory Parser
# ==========================================

def parse_inventory(
    response: dict,
    store_id: int,
    store_name: str
) -> pd.DataFrame:
    """
    Converts QueueBuster Inventory JSON response
    into the Fact_Inventory format used by Power BI.

    Parameters
    ----------
    response : dict
        Raw JSON response from QueueBuster API.

    store_id : int
        Store ID for which the API was called.

    store_name : str
        Store Name from stores.csv

    Returns
    -------
    pandas.DataFrame
    """

    # -----------------------------
    # Validate Response
    # -----------------------------
    if not response.get("status", False):
        raise ValueError("QueueBuster API returned an unsuccessful response.")

    # -----------------------------
    # Extract catalogueData
    # -----------------------------
    catalogue = response.get("catalogueData", [])

    # If store has no products
    if len(catalogue) == 0:
        return pd.DataFrame(columns=FINAL_COLUMNS)

    # -----------------------------
    # Create DataFrame
    # -----------------------------
    df = pd.DataFrame(catalogue)

    # -----------------------------
    # Keep only required columns
    # -----------------------------
    required_columns = list(COLUMN_MAPPING.keys())

    df = df[required_columns]

    # -----------------------------
    # Rename Columns
    # -----------------------------
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # -----------------------------
    # Add Store Details
    # -----------------------------
    df["StoreID"] = store_id
    df["Store Name"] = store_name

    # -----------------------------
    # Reorder Columns
    # -----------------------------
    df = df[FINAL_COLUMNS]

    return df