import pandas as pd


def parse_products(response):

    if not response.get("status"):
        raise Exception(
            response.get(
                "message",
                "Product API failed"
            )
        )

    records = response.get("data", [])

    if not records:
        raise Exception(
            "Product API returned no data."
        )

    df = pd.DataFrame(records)

    required_columns = [
        "productID",
        "productName",
        "categoryName",
        "subCategoryName",
        "brandName",
        "soldIn",
        "barcodes"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing product columns: {missing_columns}"
        )

    df = df[required_columns].copy()

    df = df.rename(
        columns={
            "productID": "product_id",
            "productName": "product_name",
            "categoryName": "category_name",
            "subCategoryName": "sub_category_name",
            "brandName": "brand_name",
            "soldIn": "unit"
        }
    )

    df["product_id"] = (
        pd.to_numeric(
            df["product_id"],
            errors="raise"
        )
        .astype(int)
    )

    df["product_name"] = (
        df["product_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["category_name"] = (
        df["category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["sub_category_name"] = (
        df["sub_category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["brand_name"] = (
        df["brand_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["unit"] = (
        df["unit"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["barcodes"] = (
        df["barcodes"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = (
        df
        .drop_duplicates(
            subset=["product_id"]
        )
        .sort_values("product_id")
        .reset_index(drop=True)
    )

    return df


def parse_product_barcodes(response):

    if not response.get("status"):
        raise Exception(
            response.get(
                "message",
                "Product API failed"
            )
        )

    records = response.get("data", [])

    if not records:
        raise Exception(
            "Product API returned no data."
        )

    rows = []

    for product in records:

        product_id = product.get("productID")

        if product_id is None:
            raise KeyError(
                "Product record missing productID"
            )

        barcodes = product.get("barcodes")

        if not barcodes:
            continue

        for barcode in str(barcodes).split(","):

            barcode = barcode.strip()

            if not barcode:
                continue

            rows.append(
                {
                    "product_id": int(product_id),
                    "barcode": barcode
                }
            )

    barcode_df = pd.DataFrame(
        rows,
        columns=[
            "product_id",
            "barcode"
        ]
    )

    if barcode_df.empty:
        return barcode_df

    barcode_df = (
        barcode_df
        .drop_duplicates()
        .sort_values(
            ["product_id", "barcode"]
        )
        .reset_index(drop=True)
    )

    return barcode_df
    