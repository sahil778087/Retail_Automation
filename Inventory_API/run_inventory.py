import pandas as pd

from time import perf_counter

from shared.auth import get_partner_token
from shared.store_loader import load_stores
from shared.inventory_parser import parse_inventory
from shared.exporter import export_inventory

from shared.database.connection import get_connection

from shared.database.repositories.run_repository import (
    create_run,
    complete_run
)

from shared.database.repositories.store_repository import (
    sync_stores
)

from shared.database.repositories.inventory_repository import (
    bulk_insert_inventory
)

from Inventory_API.qb_inventory_api import fetch_store_inventory

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

from shared.logger import get_logger
import traceback

def main():
    logger = get_logger()

    logger.info("=" * 60)
    logger.info("QUEUEBUSTER INVENTORY REFRESH")
    logger.info("=" * 60)

    # -------------------------------------------------
    # Start Timer
    # -------------------------------------------------

    start_time = perf_counter()

    # -------------------------------------------------
    # Open Database Connection
    # -------------------------------------------------

    connection = get_connection()

    # -------------------------------------------------
    # Create Inventory Run
    # -------------------------------------------------

    run_id = create_run(connection)

    logger.info(f"Run Started : {run_id}")

    # -------------------------------------------------
    # Generate Partner Token
    # -------------------------------------------------

    auth = get_partner_token()

    token = auth["token"]

    logger.info("Partner Token Generated")
    logger.info(f"Issued At : {auth['issued_at']}")
    logger.info(f"Expires   : {auth['expires']}")

    # -------------------------------------------------
    # Load Stores
    # -------------------------------------------------

    stores = load_stores()

    logger.info(f"Loaded {len(stores)} Stores")

    # -------------------------------------------------
    # Sync Store Master
    # -------------------------------------------------

    stores_synced = sync_stores(
        connection=connection,
        stores_df=stores
    )

    logger.info(f"Store Master Synced ({stores_synced} affected rows)")

    inventory_frames = []

    stores_processed = 0
    stores_failed = 0

    # -------------------------------------------------
    # Fetch Inventory
    # -------------------------------------------------

    for _, store in stores.iterrows():

        store_id = int(store["store_id"])
        store_name = str(store["store_name"])

        logger.info(f"Fetching : {store_name}")

        try:

            response = fetch_store_inventory(
                store_id=store_id,
                token=token
            )

            df = parse_inventory(
                response=response,
                store_id=store_id,
                store_name=store_name
            )

            inventory_frames.append(df)

            stores_processed += 1

            logger.info(f"Products Retrieved : {len(df)}")

        except Exception as e:

            stores_failed += 1

            logger.exception(
                f"Failed processing store: {store_name}"
            )

            continue

    # -------------------------------------------------
    # Safety Check
    # -------------------------------------------------

    if not inventory_frames:
        raise Exception("No inventory data was fetched.")

    # -------------------------------------------------
    # Merge Inventory
    # -------------------------------------------------

    final_df = pd.concat(
        inventory_frames,
        ignore_index=True
    )

# -------------------------------------------------
# Synchronize Master Tables
# -------------------------------------------------

    sync_categories(
        connection=connection,
        inventory_df=final_df
    )

    logger.info("Categories Synced")

    sync_sub_categories(
        connection=connection,
        inventory_df=final_df
    )

    logger.info("Sub Categories Synced")

    sync_brands(
        connection=connection,
        inventory_df=final_df
    )

    logger.info("Brands Synced")

    sync_products(
        connection=connection,
        inventory_df=final_df
    )

    logger.info("Products Synced")

    # -------------------------------------------------
    # Store Inventory Snapshot
    # -------------------------------------------------

    rows_inserted = bulk_insert_inventory(
        connection=connection,
        inventory_df=final_df,
        run_id=run_id
    )

    logger.info(
    f"Inventory Snapshot Inserted ({rows_inserted:,} rows)"
    )

    # -------------------------------------------------
    # Export CSV
    # -------------------------------------------------

    export_inventory(final_df)

    # -------------------------------------------------
    # Complete Inventory Run
    # -------------------------------------------------

    duration = round(
        perf_counter() - start_time,
        2
    )

    complete_run(
        connection=connection,
        run_id=run_id,
        stores_processed=stores_processed,
        stores_failed=stores_failed,
        products_processed=len(final_df),
        rows_inserted=rows_inserted,
        duration_seconds=duration
    )

    connection.commit()

    connection.close()

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    logger.info("=" * 60)
    logger.info("Inventory Refresh Completed Successfully")
    logger.info("=" * 60)

    logger.info(f"Run ID            : {run_id}")
    logger.info(f"Stores Processed  : {stores_processed}")
    logger.info(f"Stores Failed     : {stores_failed}")
    logger.info(f"Rows Inserted     : {rows_inserted:,}")
    logger.info(f"Duration          : {duration} sec")


if __name__ == "__main__":
    main()