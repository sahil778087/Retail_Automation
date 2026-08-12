"""
Master Data ETL Workflow

Fetches and synchronizes QueueBuster master data:
Categories, Subcategories, Brands, Products and Product Barcodes.
"""

from shared.auth import get_partner_token
from shared.database.connection import get_connection

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


def run_master_sync(logger):
    """
    Fetch, parse and synchronize all QueueBuster master data.

    Returns
    -------
    dict
        Synchronization statistics.
    """

    connection = None

    try:

        logger.info("=" * 60)
        logger.info("QUEUEBUSTER MASTER DATA REFRESH")
        logger.info("=" * 60)

        # -------------------------------------------------
        # Database Connection
        # -------------------------------------------------

        connection = get_connection()

        logger.info("Database Connection Opened")

        # -------------------------------------------------
        # Authentication
        # -------------------------------------------------

        auth = get_partner_token()

        token = auth["token"]

        logger.info("Partner Token Generated")

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        logger.info("Fetching Categories")

        category_response = fetch_categories(token)

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

        sub_category_response = fetch_sub_categories(token)

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

        brand_response = fetch_brands(token)

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

        product_response = fetch_products(token)

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

        category_lookup = dict(
            zip(
                category_df["category_name"],
                category_df["category_id"]
            )
        )

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
        # RESOLVE PRODUCT MASTER IDs
        # -------------------------------------------------

        product_df = product_df.merge(
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

        product_df = product_df.merge(
            sub_category_df[
                [
                    "sub_category_id",
                    "sub_category_name"
                ]
            ],
            on="sub_category_name",
            how="left",
            validate="many_to_one"
        )

        product_df = product_df.merge(
            brand_df[
                [
                    "brand_id",
                    "brand_name"
                ]
            ],
            on="brand_name",
            how="left",
            validate="many_to_one"
        )

        # -------------------------------------------------
        # RESOLVE PRODUCT MASTER IDs
        # -------------------------------------------------

        # Normalize names before matching
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
                "sub_category_id": "resolved_sub_category_id"
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
        # HANDLE MISSING MASTER INFORMATION
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

        # QueueBuster can legitimately return empty
        # category/subcategory/brand information.
        # In that case we store NULL.

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
        # KEEP ONLY PRODUCT REPOSITORY COLUMNS
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
        # COMMIT
        # -------------------------------------------------

        connection.commit()

        logger.info(
            "=" * 60
        )

        logger.info(
            "MASTER DATA REFRESH COMPLETED"
        )

        logger.info(
            "=" * 60
        )

        return {
            "categories": len(category_df),
            "sub_categories": len(sub_category_df),
            "brands": len(brand_df),
            "products": len(product_df),
            "barcodes": len(barcode_df)
        }

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Master Data Refresh Failed"
        )

        raise

    finally:

        if connection:
            connection.close()

        logger.info(
            "Database Connection Closed"
        )