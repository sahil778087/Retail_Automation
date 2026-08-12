import pandas as pd


def parse_brands(response):

    if not response.get("status"):
        raise Exception(
            response.get(
                "message",
                "Brand API failed"
            )
        )

    records = response.get("data", [])

    if not records:
        raise Exception(
            "Brand API returned no data."
        )

    df = pd.DataFrame(records)

    required_columns = [
        "brandID",
        "brandName",
        "isActive"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing brand columns: {missing_columns}"
        )

    df = df[
        required_columns
    ].copy()

    df = df.rename(
        columns={
            "brandID": "brand_id",
            "brandName": "brand_name",
            "isActive": "is_active"
        }
    )

    df["brand_id"] = (
        pd.to_numeric(
            df["brand_id"],
            errors="raise"
        )
        .astype(int)
    )

    df["brand_name"] = (
        df["brand_name"]
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
        .drop_duplicates(subset=["brand_id"])
        .sort_values("brand_id")
        .reset_index(drop=True)
    )

    return df