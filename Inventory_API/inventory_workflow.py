"""
Inventory ETL Workflow

This module contains the business workflow
for the QueueBuster Inventory ETL.
"""

import pandas as pd

from shared.auth import get_partner_token
from shared.store_loader import load_stores
from shared.inventory_parser import parse_inventory

from Inventory_API.qb_inventory_api import (
    fetch_store_inventory
)

from shared.database.repositories.inventory_repository import (
    bulk_insert_inventory
)

from time import perf_counter

from shared.database.repositories.run_repository import (
    complete_run
)

from shared.database.connection import get_connection

from shared.database.repositories.run_repository import (
    create_run
)

def fetch_inventory(logger):
    """
    Fetch inventory from all configured stores.
    """

    auth = get_partner_token()

    token = auth["token"]

    logger.info("Partner Token Generated")
    logger.info(f"Issued At : {auth['issued_at']}")
    logger.info(f"Expires   : {auth['expires']}")

    stores = load_stores()

    logger.info(f"Loaded {len(stores)} Stores")

    inventory_frames = []

    stores_processed = 0
    stores_failed = 0

    for _, store in stores.iterrows():

        store_id = int(store["store_id"])
        store_name = str(store["store_name"])

        try:

            logger.info(f"Fetching : {store_name}")



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

            logger.info(
                f"Products Retrieved : {len(df)}"
            )

        except Exception:

            stores_failed += 1

            logger.exception(
                f"Failed processing store: {store_name}"
            )

    if not inventory_frames:
        raise Exception(
            "No inventory data was fetched."
        )

    final_df = pd.concat(
        inventory_frames,
        ignore_index=True
    )

    return (
        stores,
        final_df,
        stores_processed,
        stores_failed
    )


def save_inventory_snapshot(
    connection,
    inventory_df,
    run_id,
    logger
):
    """
    Save inventory snapshot into the database.
    """

    rows_inserted = bulk_insert_inventory(
        connection=connection,
        inventory_df=inventory_df,
        run_id=run_id
    )

    logger.info(
        f"Inventory Snapshot Inserted ({rows_inserted:,} rows)"
    )

    return rows_inserted



def complete_inventory_run(
    connection,
    run_id,
    start_time,
    stores_processed,
    stores_failed,
    products_processed,
    rows_inserted,
    logger
):
    """
    Complete the inventory run and commit statistics.
    """

    duration = round(
        perf_counter() - start_time,
        2
    )

    complete_run(
        connection=connection,
        run_id=run_id,
        stores_processed=stores_processed,
        stores_failed=stores_failed,
        products_processed=products_processed,
        rows_inserted=rows_inserted,
        duration_seconds=duration
    )

    logger.info("Inventory Run Updated")

    return duration


def initialize_inventory_run(logger):
    """
    Initialize the inventory ETL run.

    Returns
    -------
    tuple
        (connection, run_id)
    """

    connection = get_connection()

    run_id = create_run(connection)

    logger.info(f"Run Started : {run_id}")

    return connection, run_id