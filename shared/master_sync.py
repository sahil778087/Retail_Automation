"""
Reusable QueueBuster Master Data Synchronization.

This module contains the actual master-data synchronization
logic so that it can be reused by:

    1. Full Master refresh
    2. Inventory recovery
    3. Sales recovery
"""

from Master_API.qb_category_api import fetch_categories
from Master_API.qb_subcategory_api import fetch_sub_categories
from Master_API.qb_brand_api import fetch_brands
from Master_API.qb_product_api import fetch_products

from shared.category_parser import parse_categories
from shared.sub_category_parser import parse_sub_categories
from shared.brand_parser import parse_brands
from shared.product_parser import (
    parse_products,
    parse_product_barcodes
)

from shared.database.repositories.category_repository import (
    sync_categories
)

from shared.database.repositories.sub_category_repository import (
    sync_sub_categories
)

from shared.database.repositories.brand_repository import (
    sync_brands
)

from shared.database.repositories.product_repository import (
    sync_products
)

from shared.database.repositories.product_barcode_repository import (
    sync_product_barcodes
)


def sync_master_data(
    connection,
    token,
    logger
):
    """
    Fetch, parse and synchronize QueueBuster master data.

    This function does NOT open or close the database connection
    and does NOT commit the transaction.

    The caller controls the transaction.

    Parameters
    ----------
    connection
        Active MySQL database connection.

    token : str
        QueueBuster partner token.

    logger
        Application logger.

    Returns
    -------
    dict
        Synchronization statistics.
    """

    # -------------------------------------------------
    # CATEGORY
    # -------------------------------------------------

    logger.info("Fetching Categories")

    category_response = fetch_categories(
        token
    )

    category_df = parse_categories(
        category_response
    )

    logger.info(
        f"Categories Prepared : {len(category_df):,}"
    )

    # -------------------------------------------------
    # SUBCATEGORY
    # -------------------------------------------------

    logger.info("Fetching Subcategories")

    sub_category_response = fetch_sub_categories(
        token
    )

    sub_category_df = parse_sub_categories(
        sub_category_response
    )

    logger.info(
        f"Subcategories Prepared : "
        f"{len(sub_category_df):,}"
    )

    # -------------------------------------------------
    # BRAND
    # -------------------------------------------------

    logger.info("Fetching Brands")

    brand_response = fetch_brands(
        token
    )

    brand_df = parse_brands(
        brand_response
    )

    logger.info(
        f"Brands Prepared : {len(brand_df):,}"
    )

    # -------------------------------------------------
    # PRODUCT
    # -------------------------------------------------

    logger.info("Fetching Products")

    product_response = fetch_products(
        token
    )

    product_df = parse_products(
        product_response
    )

    barcode_df = parse_product_barcodes(
        product_response
    )

    logger.info(
        f"Products Prepared : {len(product_df):,}"
    )

    logger.info(
        f"Product Barcodes Prepared : "
        f"{len(barcode_df):,}"
    )

    # -------------------------------------------------
    # SYNC CATEGORIES
    # -------------------------------------------------

    category_rows = sync_categories(
        connection=connection,
        category_df=category_df
    )

    logger.info(
        f"Categories Synced : {category_rows:,}"
    )

    # -------------------------------------------------
    # RESOLVE SUBCATEGORY CATEGORY IDs
    # -------------------------------------------------

    sub_category_df = sub_category_df.merge(
        category_df[
            [
                "category_id",
                "category_name"
            ]
        ],
        on="category_name",
        how="left",
        validate="many_to_one"
    )

    missing_categories = (
        sub_category_df["category_id"].isna()
    )

    if missing_categories.any():

        missing_names = (
            sub_category_df.loc[
                missing_categories,
                "category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Subcategories reference unknown "
            f"categories: {missing_names}"
        )

    sub_category_df["category_id"] = (
        sub_category_df["category_id"]
        .astype(int)
    )

    # -------------------------------------------------
    # SYNC SUBCATEGORIES
    # -------------------------------------------------

    sub_category_rows = sync_sub_categories(
        connection=connection,
        sub_categories_df=sub_category_df
    )

    logger.info(
        f"Subcategories Synced : "
        f"{sub_category_rows:,}"
    )

    # -------------------------------------------------
    # SYNC BRANDS
    # -------------------------------------------------

    brand_rows = sync_brands(
        connection=connection,
        brand_df=brand_df
    )

    logger.info(
        f"Brands Synced : {brand_rows:,}"
    )

    # -------------------------------------------------
    # NORMALIZE PRODUCT MASTER NAMES
    # -------------------------------------------------

    product_df["category_name"] = (
        product_df["category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    product_df["sub_category_name"] = (
        product_df["sub_category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    product_df["brand_name"] = (
        product_df["brand_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -------------------------------------------------
    # CATEGORY LOOKUP
    # -------------------------------------------------

    category_lookup = (
        category_df[
            [
                "category_id",
                "category_name"
            ]
        ]
        .copy()
    )

    category_lookup["category_name"] = (
        category_lookup["category_name"]
        .astype(str)
        .str.strip()
    )

    category_lookup = category_lookup.rename(
        columns={
            "category_id": "resolved_category_id"
        }
    )

    product_df = product_df.merge(
        category_lookup,
        on="category_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # SUBCATEGORY LOOKUP
    # -------------------------------------------------

    sub_category_lookup = (
        sub_category_df[
            [
                "sub_category_id",
                "sub_category_name"
            ]
        ]
        .copy()
    )

    sub_category_lookup["sub_category_name"] = (
        sub_category_lookup["sub_category_name"]
        .astype(str)
        .str.strip()
    )

    sub_category_lookup = sub_category_lookup.rename(
        columns={
            "sub_category_id":
                "resolved_sub_category_id"
        }
    )

    product_df = product_df.merge(
        sub_category_lookup,
        on="sub_category_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # BRAND LOOKUP
    # -------------------------------------------------

    brand_lookup = (
        brand_df[
            [
                "brand_id",
                "brand_name"
            ]
        ]
        .copy()
    )

    brand_lookup["brand_name"] = (
        brand_lookup["brand_name"]
        .astype(str)
        .str.strip()
    )

    brand_lookup = brand_lookup.rename(
        columns={
            "brand_id": "resolved_brand_id"
        }
    )

    product_df = product_df.merge(
        brand_lookup,
        on="brand_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # RESOLVE PRODUCT MASTER IDs
    # -------------------------------------------------

    product_df["category_id"] = (
        product_df["resolved_category_id"]
    )

    product_df["sub_category_id"] = (
        product_df["resolved_sub_category_id"]
    )

    product_df["brand_id"] = (
        product_df["resolved_brand_id"]
    )

    # -------------------------------------------------
    # HANDLE MISSING MASTER INFORMATION
    # -------------------------------------------------

    product_df.loc[
        product_df["category_name"] == "",
        "category_id"
    ] = None

    product_df.loc[
        product_df["sub_category_name"] == "",
        "sub_category_id"
    ] = None

    product_df.loc[
        product_df["brand_name"] == "",
        "brand_id"
    ] = None

    # -------------------------------------------------
    # VALIDATE CATEGORY REFERENCES
    # -------------------------------------------------

    invalid_categories = (
        (product_df["category_name"] != "")
        & (product_df["category_id"].isna())
    )

    if invalid_categories.any():

        missing_names = (
            product_df.loc[
                invalid_categories,
                "category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Products reference unknown "
            f"categories: {missing_names}"
        )

    # -------------------------------------------------
    # VALIDATE SUBCATEGORY REFERENCES
    # -------------------------------------------------

    invalid_subcategories = (
        (product_df["sub_category_name"] != "")
        & (product_df["sub_category_id"].isna())
    )

    if invalid_subcategories.any():

        missing_names = (
            product_df.loc[
                invalid_subcategories,
                "sub_category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Products reference unknown "
            f"subcategories: {missing_names}"
        )

    # -------------------------------------------------
    # VALIDATE BRAND REFERENCES
    # -------------------------------------------------

    invalid_brands = (
        (product_df["brand_name"] != "")
        & (product_df["brand_id"].isna())
    )

    if invalid_brands.any():

        missing_names = (
            product_df.loc[
                invalid_brands,
                "brand_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Products reference unknown "
            f"brands: {missing_names}"
        )

    # -------------------------------------------------
    # PRIMARY BARCODE
    # -------------------------------------------------

    product_df["barcode"] = (
        product_df["barcodes"]
        .apply(
            lambda value:
                str(value).split(",")[0].strip()
                if value
                else None
        )
    )

    # -------------------------------------------------
    # KEEP PRODUCT REPOSITORY COLUMNS
    # -------------------------------------------------

    product_df = product_df[
        [
            "product_id",
            "product_name",
            "category_id",
            "sub_category_id",
            "brand_id",
            "barcode",
            "unit"
        ]
    ].copy()

    # -------------------------------------------------
    # SYNC PRODUCTS
    # -------------------------------------------------

    product_rows = sync_products(
        connection=connection,
        product_df=product_df
    )

    logger.info(
        f"Products Synced : {product_rows:,}"
    )

    # -------------------------------------------------
    # SYNC PRODUCT BARCODES
    # -------------------------------------------------

    barcode_rows = sync_product_barcodes(
        connection=connection,
        barcode_df=barcode_df
    )

    logger.info(
        f"Product Barcodes Synced : "
        f"{barcode_rows:,}"
    )

    # -------------------------------------------------
    # RETURN STATISTICS
    # -------------------------------------------------

    return {
        "categories": len(category_df),
        "sub_categories": len(sub_category_df),
        "brands": len(brand_df),
        "products": len(product_df),
        "barcodes": len(barcode_df)
    }

def ensure_products_exist(
    connection,
    product_ids,
    token,
    logger
):
    """
    Ensure that legitimate QueueBuster products exist
    in the local product master.

    Negative product IDs are ignored because they are
    known beta-environment artifacts.

    Parameters
    ----------
    connection
        Active MySQL connection.

    product_ids : iterable
        Product IDs that need to be checked.

    token : str
        QueueBuster partner token.

    logger
        Application logger.

    Returns
    -------
    list
        Product IDs successfully ensured.
    """

    # -------------------------------------------------
    # NORMALIZE PRODUCT IDS
    # -------------------------------------------------

    product_ids = {
        int(product_id)
        for product_id in product_ids
        if product_id is not None
    }

    if not product_ids:
        return []

    # -------------------------------------------------
    # IGNORE NEGATIVE BETA PRODUCT IDs
    # -------------------------------------------------

    negative_ids = {
        product_id
        for product_id in product_ids
        if product_id < 0
    }

    if negative_ids:

        logger.info(
            "Ignoring beta product IDs : "
            f"{sorted(negative_ids)}"
        )

    product_ids = {
        product_id
        for product_id in product_ids
        if product_id >= 0
    }

    if not product_ids:
        return []

    # -------------------------------------------------
    # CHECK LOCAL PRODUCT MASTER
    # -------------------------------------------------

    cursor = connection.cursor()

    placeholders = ", ".join(
        ["%s"] * len(product_ids)
    )

    query = f"""
        SELECT product_id
        FROM product
        WHERE product_id IN ({placeholders})
    """

    cursor.execute(
        query,
        tuple(product_ids)
    )

    existing_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

    cursor.close()

    # -------------------------------------------------
    # DETERMINE MISSING PRODUCTS
    # -------------------------------------------------

    missing_ids = product_ids - existing_ids

    if not missing_ids:

        logger.info(
            "All requested products already exist."
        )

        return sorted(existing_ids)

    logger.info(
        "Missing Product IDs : "
        f"{sorted(missing_ids)}"
    )

    # -------------------------------------------------
    # FETCH CURRENT PRODUCT MASTER
    # -------------------------------------------------

    logger.info(
        "Fetching Product Master for recovery"
    )

    product_response = fetch_products(
        token
    )

    product_df = parse_products(
        product_response
    )

    barcode_df = parse_product_barcodes(
        product_response
    )

    # -------------------------------------------------
    # FIND REQUESTED PRODUCTS
    # -------------------------------------------------

    recovery_products = product_df[
        product_df["product_id"].isin(
            missing_ids
        )
    ].copy()

    if recovery_products.empty:

        raise ValueError(
            "QueueBuster Product API did not return "
            f"requested products: "
            f"{sorted(missing_ids)}"
        )

    found_ids = set(
        recovery_products["product_id"]
    )

    unresolved_ids = (
        missing_ids - found_ids
    )

    if unresolved_ids:

        raise ValueError(
            "QueueBuster Product API did not return "
            f"products: {sorted(unresolved_ids)}"
        )

    logger.info(
        "Products Found For Recovery : "
        f"{len(recovery_products)}"
    )

    # -------------------------------------------------
    # FETCH MASTER DEPENDENCIES
    # -------------------------------------------------

    logger.info(
        "Fetching Master Dependencies for recovery"
    )

    # -------------------------------------------------
    # CATEGORIES
    # -------------------------------------------------

    category_response = fetch_categories(
        token
    )

    category_df = parse_categories(
        category_response
    )

    sync_categories(
        connection=connection,
        category_df=category_df
    )

    # -------------------------------------------------
    # SUBCATEGORIES
    # -------------------------------------------------

    sub_category_response = fetch_sub_categories(
        token
    )

    sub_category_df = parse_sub_categories(
        sub_category_response
    )

    sub_category_df = sub_category_df.merge(
        category_df[
            [
                "category_id",
                "category_name"
            ]
        ],
        on="category_name",
        how="left",
        validate="many_to_one"
    )

    missing_categories = (
        sub_category_df["category_id"].isna()
    )

    if missing_categories.any():

        missing_names = (
            sub_category_df.loc[
                missing_categories,
                "category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Subcategories reference unknown "
            f"categories during recovery: "
            f"{missing_names}"
        )

    sub_category_df["category_id"] = (
        sub_category_df["category_id"].astype(int)
    )

    sync_sub_categories(
        connection=connection,
        sub_categories_df=sub_category_df
    )

    # -------------------------------------------------
    # BRANDS
    # -------------------------------------------------

    brand_response = fetch_brands(
        token
    )

    brand_df = parse_brands(
        brand_response
    )

    sync_brands(
        connection=connection,
        brand_df=brand_df
    )

    # -------------------------------------------------
    # NORMALIZE RECOVERY PRODUCTS
    # -------------------------------------------------

    recovery_products["category_name"] = (
        recovery_products["category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    recovery_products["sub_category_name"] = (
        recovery_products["sub_category_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    recovery_products["brand_name"] = (
        recovery_products["brand_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -------------------------------------------------
    # CATEGORY LOOKUP
    # -------------------------------------------------

    category_lookup = (
        category_df[
            [
                "category_id",
                "category_name"
            ]
        ]
        .copy()
    )

    category_lookup["category_name"] = (
        category_lookup["category_name"]
        .astype(str)
        .str.strip()
    )

    category_lookup = category_lookup.rename(
        columns={
            "category_id": "resolved_category_id"
        }
    )

    recovery_products = recovery_products.merge(
        category_lookup,
        on="category_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # SUBCATEGORY LOOKUP
    # -------------------------------------------------

    sub_category_lookup = (
        sub_category_df[
            [
                "sub_category_id",
                "sub_category_name"
            ]
        ]
        .copy()
    )

    sub_category_lookup["sub_category_name"] = (
        sub_category_lookup["sub_category_name"]
        .astype(str)
        .str.strip()
    )

    sub_category_lookup = sub_category_lookup.rename(
        columns={
            "sub_category_id":
                "resolved_sub_category_id"
        }
    )

    recovery_products = recovery_products.merge(
        sub_category_lookup,
        on="sub_category_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # BRAND LOOKUP
    # -------------------------------------------------

    brand_lookup = (
        brand_df[
            [
                "brand_id",
                "brand_name"
            ]
        ]
        .copy()
    )

    brand_lookup["brand_name"] = (
        brand_lookup["brand_name"]
        .astype(str)
        .str.strip()
    )

    brand_lookup = brand_lookup.rename(
        columns={
            "brand_id": "resolved_brand_id"
        }
    )

    recovery_products = recovery_products.merge(
        brand_lookup,
        on="brand_name",
        how="left",
        validate="many_to_one"
    )

    # -------------------------------------------------
    # ASSIGN RESOLVED IDS
    # -------------------------------------------------

    recovery_products["category_id"] = (
        recovery_products["resolved_category_id"]
    )

    recovery_products["sub_category_id"] = (
        recovery_products["resolved_sub_category_id"]
    )

    recovery_products["brand_id"] = (
        recovery_products["resolved_brand_id"]
    )

    # -------------------------------------------------
    # HANDLE EMPTY MASTER REFERENCES
    # -------------------------------------------------

    recovery_products.loc[
        recovery_products["category_name"] == "",
        "category_id"
    ] = None

    recovery_products.loc[
        recovery_products["sub_category_name"] == "",
        "sub_category_id"
    ] = None

    recovery_products.loc[
        recovery_products["brand_name"] == "",
        "brand_id"
    ] = None

    # -------------------------------------------------
    # VALIDATE CATEGORY
    # -------------------------------------------------

    invalid_categories = (
        (recovery_products["category_name"] != "")
        & (recovery_products["category_id"].isna())
    )

    if invalid_categories.any():

        missing_names = (
            recovery_products.loc[
                invalid_categories,
                "category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Recovery products reference unknown "
            f"categories: {missing_names}"
        )

    # -------------------------------------------------
    # VALIDATE SUBCATEGORY
    # -------------------------------------------------

    invalid_subcategories = (
        (recovery_products["sub_category_name"] != "")
        & (recovery_products["sub_category_id"].isna())
    )

    if invalid_subcategories.any():

        missing_names = (
            recovery_products.loc[
                invalid_subcategories,
                "sub_category_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Recovery products reference unknown "
            f"subcategories: {missing_names}"
        )

    # -------------------------------------------------
    # VALIDATE BRAND
    # -------------------------------------------------

    invalid_brands = (
        (recovery_products["brand_name"] != "")
        & (recovery_products["brand_id"].isna())
    )

    if invalid_brands.any():

        missing_names = (
            recovery_products.loc[
                invalid_brands,
                "brand_name"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Recovery products reference unknown "
            f"brands: {missing_names}"
        )

    # -------------------------------------------------
    # PRIMARY BARCODE
    # -------------------------------------------------

    recovery_products["barcode"] = (
        recovery_products["barcodes"]
        .apply(
            lambda value:
                str(value).split(",")[0].strip()
                if value
                else None
        )
    )

    # -------------------------------------------------
    # KEEP PRODUCT COLUMNS
    # -------------------------------------------------

    recovery_products = recovery_products[
        [
            "product_id",
            "product_name",
            "category_id",
            "sub_category_id",
            "brand_id",
            "barcode",
            "unit"
        ]
    ].copy()

    # -------------------------------------------------
    # SYNC RECOVERED PRODUCTS
    # -------------------------------------------------

    product_rows = sync_products(
        connection=connection,
        product_df=recovery_products
    )

    logger.info(
        f"Recovered Products Synced : "
        f"{product_rows:,}"
    )

    # -------------------------------------------------
    # SYNC RECOVERED BARCODES
    # -------------------------------------------------

    recovery_barcodes = barcode_df[
        barcode_df["product_id"].isin(
            missing_ids
        )
    ].copy()

    if not recovery_barcodes.empty:

        barcode_rows = sync_product_barcodes(
            connection=connection,
            barcode_df=recovery_barcodes
        )

        logger.info(
            f"Recovered Barcodes Synced : "
            f"{barcode_rows:,}"
        )

    # -------------------------------------------------
    # RETURN
    # -------------------------------------------------

    return sorted(
        existing_ids | found_ids
    )