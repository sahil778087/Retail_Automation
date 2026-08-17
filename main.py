import sys
from datetime import datetime
from time import perf_counter

from shared.logger import get_logger
from shared.config import validate_config

from Inventory_API.run_inventory import main as run_inventory
from Master_API.run_master import main as run_master
from Sales_API.run_sales import main as run_sales


def resolve_sales_date():

    if len(sys.argv) == 3:

        sales_date = sys.argv[2]

        try:

            datetime.strptime(
                sales_date,
                "%Y-%m-%d"
            )

        except ValueError:

            raise ValueError(
                "Invalid date format. "
                "Use YYYY-MM-DD."
            )

    else:

        sales_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    return sales_date


def main():

    # -------------------------------------------------
    # Argument Validation
    # -------------------------------------------------

    if len(sys.argv) < 2 or len(sys.argv) > 3:

        raise ValueError(
            "Usage: python main.py "
            "[inventory|sales|master|all] "
            "[YYYY-MM-DD]"
        )

    process = sys.argv[1].lower()

    # -------------------------------------------------
    # Configuration Validation
    # -------------------------------------------------

    validate_config()

    logger = get_logger()

    start_time = perf_counter()

    logger.info("=" * 60)
    logger.info("RETAIL AUTOMATION STARTED")
    logger.info("=" * 60)

    logger.info(
        f"Process : {process.upper()}"
    )

    try:

        # =================================================
        # INVENTORY
        # =================================================

        if process == "inventory":

            logger.info(
                "Starting Inventory Refresh"
            )

            run_inventory()

            logger.info(
                "Inventory Refresh Successful"
            )

        # =================================================
        # SALES
        # =================================================

        elif process == "sales":

            sales_date = resolve_sales_date()

            logger.info(
                f"Starting Sales Refresh | "
                f"Date={sales_date}"
            )

            run_sales(
                sales_date=sales_date
            )

            logger.info(
                "Sales Refresh Successful"
            )

        # =================================================
        # MASTER
        # =================================================

        elif process == "master":

            logger.info(
                "Starting Master Refresh"
            )

            run_master()

            logger.info(
                "Master Refresh Successful"
            )

        # =================================================
        # ALL
        # =================================================

        elif process == "all":

            sales_date = resolve_sales_date()

            logger.info(
                f"Starting Full Retail ETL | "
                f"Sales Date={sales_date}"
            )

            # -------------------------------------------------
            # 1. MASTER
            # -------------------------------------------------

            logger.info(
                "=" * 60
            )

            logger.info(
                "STEP 1/3 | MASTER DATA"
            )

            logger.info(
                "=" * 60
            )

            run_master()

            logger.info(
                "STEP 1/3 | MASTER SUCCESS"
            )

            # -------------------------------------------------
            # 2. SALES
            # -------------------------------------------------

            logger.info(
                "=" * 60
            )

            logger.info(
                "STEP 2/3 | SALES"
            )

            logger.info(
                "=" * 60
            )

            run_sales(
                sales_date=sales_date
            )

            logger.info(
                "STEP 2/3 | SALES SUCCESS"
            )

            # -------------------------------------------------
            # 3. INVENTORY
            # -------------------------------------------------

            logger.info(
                "=" * 60
            )

            logger.info(
                "STEP 3/3 | INVENTORY"
            )

            logger.info(
                "=" * 60
            )

            run_inventory()

            logger.info(
                "STEP 3/3 | INVENTORY SUCCESS"
            )

            logger.info(
                "=" * 60
            )

            logger.info(
                "ALL RETAIL ETL PROCESSES SUCCESSFUL"
            )

            logger.info(
                "=" * 60
            )

        # =================================================
        # INVALID PROCESS
        # =================================================

        else:

            raise ValueError(
                f"Unknown process: {process}. "
                "Use inventory, sales, master, or all."
            )

        # -------------------------------------------------
        # Overall Success
        # -------------------------------------------------

        duration = round(
            perf_counter() - start_time,
            2
        )

        logger.info(
            f"RETAIL AUTOMATION COMPLETED | "
            f"Duration={duration} sec"
        )

        return 0

    except Exception:

        duration = round(
            perf_counter() - start_time,
            2
        )

        logger.exception(
            f"RETAIL AUTOMATION FAILED | "
            f"Duration={duration} sec"
        )

        raise


if __name__ == "__main__":

    main()