from shared.database.connection import get_connection
from shared.database.repositories.sales_repository import bulk_insert_sales
from shared.logger import get_logger
from Sales_API.sales_workflow import fetch_sales_for_date


def main():

    logger = get_logger()

    connection = get_connection()

    sales_df = fetch_sales_for_date(
        sales_date="2026-07-30",
        logger=logger
    )

    rows = bulk_insert_sales(
        connection=connection,
        sales_df=sales_df
    )

    connection.commit()

    print(f"\nRows affected: {rows}")

    connection.close()


if __name__ == "__main__":
    main()