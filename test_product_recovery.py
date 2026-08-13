from shared.auth import get_partner_token
from shared.database.connection import get_connection
from shared.master_sync import ensure_products_exist
from shared.logger import get_logger


def main():

    logger = get_logger()

    connection = get_connection()

    try:

        auth = get_partner_token()

        token = auth["token"]

        # Use one product that already exists
        # and one known product from QueueBuster
        product_ids = [
            101
        ]

        result = ensure_products_exist(
            connection=connection,
            product_ids=product_ids,
            token=token,
            logger=logger
        )

        connection.commit()

        print(
            "Recovered / Verified Products:",
            result
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()