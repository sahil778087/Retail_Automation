import pandas as pd

from time import perf_counter

from shared.auth import get_partner_token
from shared.store_loader import load_stores
from shared.inventory_parser import parse_inventory
from shared.exporter import export_inventory

from shared.database.repositories.run_repository import (
    fail_run
)

from shared.database.repositories.store_repository import (
    sync_stores
)

from Inventory_API.qb_inventory_api import fetch_store_inventory

from Inventory_API.inventory_workflow import (
    initialize_inventory_run,
    fetch_inventory,
    recover_inventory_products,
    save_inventory_snapshot,
    complete_inventory_run
)

from shared.logger import get_logger

def main():
    logger = get_logger()

    logger.info("=" * 60)
    logger.info("QUEUEBUSTER INVENTORY REFRESH")
    logger.info("=" * 60)

    # -------------------------------------------------
    # Start Timer
    # -------------------------------------------------

    start_time = perf_counter()

    connection = None
    run_id = None
    rows_inserted = 0
    stores_processed = 0
    stores_failed = 0

# -------------------------------------------------
# initialize_inventory_run
# -------------------------------------------------
    try:
        connection, run_id = initialize_inventory_run(
        logger=logger
        )



    # -------------------------------------------------
    # Fetch Inventory
    # -------------------------------------------------

        stores, final_df, stores_processed, stores_failed, token = fetch_inventory(
            logger=logger
        )

        # -------------------------------------------------
        # Sync Store Master
        # -------------------------------------------------

        stores_synced = sync_stores(
            connection=connection,
            stores_df=stores
        )

        logger.info(
            f"Store Master Synced ({stores_synced} affected rows)"
        )

        # -------------------------------------------------
        # Recover Missing Product Master Data
        # -------------------------------------------------

        recover_inventory_products(
            connection=connection,
            inventory_df=final_df,
            token=token,
            logger=logger
        )

        # -------------------------------------------------
        # Store Inventory Snapshot
        # -------------------------------------------------

        rows_inserted = save_inventory_snapshot(
            connection=connection,
            inventory_df=final_df,
            run_id=run_id,
            logger=logger
        )

        # -------------------------------------------------
        # Export CSV
        # -------------------------------------------------

        export_inventory(final_df)

        # -------------------------------------------------
        # Complete Inventory Run
        # -------------------------------------------------

        duration = complete_inventory_run(
            connection=connection,
            run_id=run_id,
            start_time=start_time,
            stores_processed=stores_processed,
            stores_failed=stores_failed,
            products_processed=len(final_df),
            rows_inserted=rows_inserted,
            logger=logger
        )

        connection.commit()


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

    except Exception as e:

        logger.exception("Inventory ETL Failed")

        if connection is not None:

            connection.rollback()

            logger.info("Database Transaction Rolled Back")

            if run_id is not None:

                fail_run(
                    connection=connection,
                    run_id=run_id
                )

                connection.commit()

                logger.info("Inventory Run Marked As FAILED")
    finally:

        if connection is not None and connection.is_connected():

            connection.close()

            logger.info("Database Connection Closed")


if __name__ == "__main__":
    main()