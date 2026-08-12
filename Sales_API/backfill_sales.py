import sys
from datetime import datetime, timedelta
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
    # Validate Command Line Arguments
    # -------------------------------------------------

    if len(sys.argv) != 3:

        raise ValueError(
            "Usage: "
            "python -m Sales_API.backfill_sales "
            "YYYY-MM-DD YYYY-MM-DD"
        )

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    # -------------------------------------------------
    # Validate Dates
    # -------------------------------------------------

    try:

        start = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        raise ValueError(
            "Dates must be in YYYY-MM-DD format."
        )

    if start > end:

        raise ValueError(
            "Start date cannot be after end date."
        )

    # -------------------------------------------------
    # Start Backfill
    # -------------------------------------------------

    logger.info("=" * 60)
    logger.info("QUEUEBUSTER SALES HISTORICAL BACKFILL")
    logger.info("=" * 60)

    logger.info(
        f"Backfill Range : {start_date} → {end_date}"
    )

    try:

        connection = get_connection()

        current_date = start

        total_rows = 0
        total_days = 0

        while current_date <= end:

            sales_date = current_date.strftime(
                "%Y-%m-%d"
            )

            logger.info("-" * 60)
            logger.info(
                f"Processing Sales Date : {sales_date}"
            )

            # -------------------------------------------------
            # Fetch & Prepare Sales
            # -------------------------------------------------

            sales_df, checkpoint_updates = (
                fetch_sales_for_date(
                    sales_date=sales_date,
                    logger=logger
                )
            )

            logger.info(
                f"Rows Prepared : {len(sales_df):,}"
            )

            # -------------------------------------------------
            # Insert Sales
            # -------------------------------------------------

            rows_affected = bulk_insert_sales(
                connection=connection,
                sales_df=sales_df
            )

            logger.info(
                f"Rows Inserted/Updated : "
                f"{rows_affected:,}"
            )

            # -------------------------------------------------
            # Update Checkpoints
            # -------------------------------------------------

            for store_id, checkpoint in (
                checkpoint_updates.items()
            ):

                last_order_id, last_order_time = checkpoint

                update_sales_checkpoint(
                    connection=connection,
                    store_id=store_id,
                    sales_date=sales_date,
                    last_order_id=last_order_id,
                    last_order_time=last_order_time
                )

            logger.info(
                f"Checkpoints Updated : "
                f"{len(checkpoint_updates)} stores"
            )

            # -------------------------------------------------
            # Commit This Date
            # -------------------------------------------------

            connection.commit()

            total_rows += rows_affected
            total_days += 1

            current_date += timedelta(days=1)

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        duration = round(
            perf_counter() - start_time,
            2
        )

        logger.info("=" * 60)
        logger.info(
            "SALES HISTORICAL BACKFILL COMPLETED"
        )
        logger.info("=" * 60)

        logger.info(
            f"Days Processed : {total_days}"
        )

        logger.info(
            f"Rows Inserted/Updated : {total_rows:,}"
        )

        logger.info(
            f"Duration : {duration} sec"
        )

    except Exception:

        if connection:

            connection.rollback()

            logger.info(
                "Database Transaction Rolled Back"
            )

        logger.exception(
            "Sales Historical Backfill Failed"
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