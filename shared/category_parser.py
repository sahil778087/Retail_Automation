import pandas as pd


def parse_categories(response):

    if not response.get("status"):
        raise Exception(
            response.get(
                "message",
                "Category API failed"
            )
        )

    records = response.get("data", [])

    if not records:
        raise Exception(
            "Category API returned no data."
        )

    df = pd.DataFrame(records)

    required_columns = [
        "categoryID",
        "categoryName",
        "isActive"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing category columns: {missing_columns}"
        )

    df = df[
        required_columns
    ].copy()

    df = df.rename(
        columns={
            "categoryID": "category_id",
            "categoryName": "category_name",
            "isActive": "is_active"
        }
    )

    df["category_id"] = (
        pd.to_numeric(
            df["category_id"],
            errors="raise"
        )
        .astype(int)
    )

    df["category_name"] = (
        df["category_name"]
        .astype(str)
        .str.strip()
    )

    df["is_active"] = (
        pd.to_numeric(
            df["is_active"],
            errors="raise"
        )
        .astype(int)
    )

    df = (
        df
        .drop_duplicates(subset=["category_id"])
        .sort_values("category_id")
        .reset_index(drop=True)
    )

    return df