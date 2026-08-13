"""
Master Data ETL Workflow

Controls the QueueBuster Master Data refresh.
"""

from shared.auth import get_partner_token
from shared.database.connection import get_connection
from shared.master_sync import sync_master_data


def run_master_sync(logger):
    """
    Run the complete QueueBuster Master Data refresh.

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
        # DATABASE CONNECTION
        # -------------------------------------------------

        connection = get_connection()

        logger.info(
            "Database Connection Opened"
        )

        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------

        auth = get_partner_token()

        token = auth["token"]

        logger.info(
            "Partner Token Generated"
        )

        # -------------------------------------------------
        # MASTER SYNCHRONIZATION
        # -------------------------------------------------

        results = sync_master_data(
            connection=connection,
            token=token,
            logger=logger
        )

        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------

        connection.commit()

        logger.info("=" * 60)
        logger.info(
            "MASTER DATA REFRESH COMPLETED"
        )
        logger.info("=" * 60)

        return results

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