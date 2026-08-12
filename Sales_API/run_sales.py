import sys
from datetime import datetime
from time import perf_counter

from shared.logger import get_logger
from shared.database.connection import get_connection

from Sales_API.sales_workflow import fetch_sales_for_date

from shared.database.repositories.sales_repository import (
    bulk_insert_sales,
    update_sales_checkpoint
)


def main():

    logger = get_logger()

    start_time = perf_counter()

    connection = None

    # -------------------------------------------------
    # Validate Command Line Argument
    # -------------------------------------------------

    if len(sys.argv) != 2:
        raise ValueError(
            "Usage: python -m Sales_API.run_sales YYYY-MM-DD"
        )

    sales_date = sys.argv[1]

    # -------------------------------------------------
    # Validate Sales Date
    # -------------------------------------------------

    try:

        datetime.strptime(
            sales_date,
            "%Y-%m-%d"
        )

    except ValueError:

        raise ValueError(
            f"Invalid sales date: {sales_date}. "
            "Expected format: YYYY-MM-DD"
        )

    # -------------------------------------------------
    # Start Sales ETL
    # -------------------------------------------------

    try:

        logger.info("=" * 60)
        logger.info("QUEUEBUSTER SALES REFRESH")
        logger.info("=" * 60)

        logger.info(
            f"Sales Date : {sales_date}"
        )

        # -------------------------------------------------
        # Open Database Connection
        # -------------------------------------------------

        connection = get_connection()

        # -------------------------------------------------
        # Fetch & Parse Sales
        # -------------------------------------------------

        sales_df, checkpoint_updates = fetch_sales_for_date(
            sales_date=sales_date,
            logger=logger
        )

        logger.info(
            f"Sales Rows Prepared : {len(sales_df):,}"
        )

        # -------------------------------------------------
        # Insert Sales
        # -------------------------------------------------

        rows_affected = bulk_insert_sales(
            connection=connection,
            sales_df=sales_df
        )

        logger.info(
            f"Sales Rows Inserted/Updated : {rows_affected:,}"
        )

        # -------------------------------------------------
        # Update Sales Checkpoints
        # -------------------------------------------------

        for store_id, checkpoint in checkpoint_updates.items():

            last_order_id, last_order_time = checkpoint

            update_sales_checkpoint(
                connection=connection,
                store_id=store_id,
                sales_date=sales_date,
                last_order_id=last_order_id,
                last_order_time=last_order_time
            )

        logger.info(
            f"Sales Checkpoints Updated : "
            f"{len(checkpoint_updates)} stores"
        )

        # -------------------------------------------------
        # Commit
        # -------------------------------------------------

        connection.commit()

        duration = round(
            perf_counter() - start_time,
            2
        )

        logger.info(
            f"Sales Refresh Completed : {duration} sec"
        )

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Sales ETL Failed"
        )

        raise

    finally:

        if connection:
            connection.close()

        logger.info(
            "Database Connection Closed"
        )


if __name__ == "__main__":
    main()