import sys
from time import perf_counter

from shared.logger import get_logger
from Master_API.master_workflow import run_master_sync


def main():

    logger = get_logger()

    start_time = perf_counter()

    try:

        results = run_master_sync(
            logger=logger
        )

        duration = round(
            perf_counter() - start_time,
            2
        )

        logger.info(
            f"Categories : {results['categories']:,}"
        )

        logger.info(
            f"Subcategories : "
            f"{results['sub_categories']:,}"
        )

        logger.info(
            f"Brands : {results['brands']:,}"
        )

        logger.info(
            f"Products : {results['products']:,}"
        )

        logger.info(
            f"Barcodes : {results['barcodes']:,}"
        )

        logger.info(
            f"Master Refresh Completed : "
            f"{duration} sec"
        )

    except Exception:

        logger.exception(
            "Master Refresh Failed"
        )

        raise


if __name__ == "__main__":
    main()