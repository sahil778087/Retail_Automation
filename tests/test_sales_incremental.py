from shared.logger import get_logger

from Sales_API.sales_workflow import (
    fetch_sales_for_date
)


def main():

    logger = get_logger()

    sales_df, checkpoint_updates = fetch_sales_for_date(
        sales_date="2026-07-30",
        logger=logger
    )

    print("\nRows:")
    print(len(sales_df))

    print("\nRows by Store:")
    print(
        sales_df["store_id"].value_counts()
    )

    print("\nCheckpoint Updates:")
    for store_id, checkpoint in checkpoint_updates.items():
        print(
            store_id,
            "->",
            checkpoint
        )


if __name__ == "__main__":
    main()