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
from shared.master_sync import ensure_products_exist

from shared.alert_service import process_inventory_alert

from shared.database.repositories.demand_repository import (
    save_7_day_thresholds
)

from shared.database.repositories.alert_repository import (
    get_alert_thresholds
)

def recover_inventory_products(
    connection,
    inventory_df,
    token,
    logger
):
    """
    Ensure all legitimate inventory products exist
    in the local product master.
    """

    product_ids = (
        inventory_df["product_id"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if not product_ids:
        return []

    logger.info(
        f"Checking Inventory Product Master : "
        f"{len(product_ids)} products"
    )

    recovered_products = ensure_products_exist(
        connection=connection,
        product_ids=product_ids,
        token=token,
        logger=logger
    )

    logger.info(
        f"Inventory Product Master Check Completed : "
        f"{len(recovered_products)} products"
    )

    return recovered_products

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
        stores_failed,
        token
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

def update_inventory_alert_thresholds(
    connection,
    logger
):
    """
    Calculate and save 7-day demand thresholds
    before inventory alert evaluation.
    """

    from datetime import date

    result = save_7_day_thresholds(
        connection=connection,
        reference_date=date.today()
    )

    thresholds_count = len(
        result["thresholds"]
    )

    rows_affected = result["updated_rows"]

    logger.info(
        f"Inventory Alert Thresholds Updated : "
        f"{thresholds_count}"
    )

    logger.info(
        f"Threshold Rows Affected : "
        f"{rows_affected}"
    )

    return result


def evaluate_inventory_alerts(
    connection,
    run_id,
    inventory_df,
    logger
):
    """
    Evaluate inventory alerts for the current
    inventory snapshot.
    """

    # -------------------------------------------------
    # Load Active Thresholds
    # -------------------------------------------------

    threshold_rows = get_alert_thresholds(
        connection=connection
    )

    # -------------------------------------------------
    # Convert Thresholds Into Lookup Dictionary
    # -------------------------------------------------

    threshold_map = {
        (
            int(row["store_id"]),
            int(row["product_id"])
        ): row["threshold_quantity"]
        for row in threshold_rows
    }

    logger.info(
        f"Active Alert Thresholds Loaded : "
        f"{len(threshold_map):,}"
    )

    # -------------------------------------------------
    # Alert Counters
    # -------------------------------------------------

    alerts_created = 0
    alerts_resolved = 0
    alerts_kept_open = 0
    products_without_threshold = 0

    # -------------------------------------------------
    # Evaluate Inventory
    # -------------------------------------------------

    for row in inventory_df.itertuples(index=False):

        store_id = int(row.store_id)
        product_id = int(row.product_id)
        stock_quantity = row.stock_quantity

        threshold_quantity = threshold_map.get(
            (store_id, product_id)
        )

        # -------------------------------------------------
        # No Threshold
        # -------------------------------------------------

        if threshold_quantity is None:

            products_without_threshold += 1

            continue

        # -------------------------------------------------
        # Evaluate Alert
        # -------------------------------------------------

        result = process_inventory_alert(
            connection=connection,
            run_id=run_id,
            store_id=store_id,
            product_id=product_id,
            stock_quantity=stock_quantity,
            threshold_quantity=threshold_quantity,
            logger=logger
        )

        action = result["action"]

        if action == "CREATED":

            alerts_created += 1

        elif action == "RESOLVED":

            alerts_resolved += 1

        elif action == "KEEP_OPEN":

            alerts_kept_open += 1

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    logger.info(
        f"Alerts Created : {alerts_created}"
    )

    logger.info(
        f"Alerts Resolved : {alerts_resolved}"
    )

    logger.info(
        f"Alerts Kept Open : {alerts_kept_open}"
    )

    logger.info(
        f"Products Without Threshold : "
        f"{products_without_threshold}"
    )

    return {
        "created": alerts_created,
        "resolved": alerts_resolved,
        "kept_open": alerts_kept_open,
        "without_threshold": products_without_threshold
    }

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

    The run record is committed immediately so that
    a later ETL failure can safely mark this run as FAILED.
    """

    connection = get_connection()

    run_id = create_run(connection)

    # -------------------------------------------------
    # Commit RUNNING status
    # -------------------------------------------------

    connection.commit()

    logger.info(
        f"Run Started : {run_id}"
    )

    return connection, run_id