from shared.database.connection import get_connection

from shared.database.repositories.sales_repository import (
    get_sales_checkpoint,
    update_sales_checkpoint
)


def main():

    connection = get_connection()

    store_id = 99142450
    sales_date = "2026-08-08"

    checkpoint = get_sales_checkpoint(
        connection=connection,
        store_id=store_id,
        sales_date=sales_date
    )

    print("\nInitial checkpoint:")
    print(checkpoint)

    update_sales_checkpoint(
        connection=connection,
        store_id=store_id,
        sales_date=sales_date,
        last_order_id="TEST-ORDER-001",
        last_order_time="2026-08-08 10:00:00"
    )

    connection.commit()

    checkpoint = get_sales_checkpoint(
        connection=connection,
        store_id=store_id,
        sales_date=sales_date
    )

    print("\nUpdated checkpoint:")
    print(checkpoint)

    connection.close()


if __name__ == "__main__":
    main()