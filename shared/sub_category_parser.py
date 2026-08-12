import pandas as pd


def parse_sub_categories(response):

    if not response.get("status"):
        raise Exception(
            response.get(
                "message",
                "Subcategory API failed"
            )
        )

    records = response.get("data", [])

    if not records:
        raise Exception(
            "Subcategory API returned no data."
        )

    df = pd.DataFrame(records)

    required_columns = [
        "subCategoryID",
        "subCategoryName",
        "categoryName"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing subcategory columns: {missing_columns}"
        )

    df = df[
        required_columns
    ].copy()

    df = df.rename(
        columns={
            "subCategoryID": "sub_category_id",
            "subCategoryName": "sub_category_name",
            "categoryName": "category_name"
        }
    )

    df["sub_category_id"] = (
        pd.to_numeric(
            df["sub_category_id"],
            errors="raise"
        )
        .astype(int)
    )

    df["sub_category_name"] = (
        df["sub_category_name"]
        .astype(str)
        .str.strip()
    )

    df["category_name"] = (
        df["category_name"]
        .astype(str)
        .str.strip()
    )

    df = (
        df
        .drop_duplicates(subset=["sub_category_id"])
        .sort_values("sub_category_id")
        .reset_index(drop=True)
    )

    return df