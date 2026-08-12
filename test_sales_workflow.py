from shared.logger import get_logger
from Sales_API.sales_workflow import fetch_sales_for_date


def main():

    logger = get_logger()

    sales_df = fetch_sales_for_date(
        sales_date="2026-07-30",
        logger=logger
    )

    print("\nSales DataFrame:")
    print(sales_df.head())

    print("\nColumns:")
    print(sales_df.columns.tolist())

    print("\nRows:")
    print(len(sales_df))

    print("\nRows by Store:")
    print(sales_df["store_id"].value_counts())

    print("\nSample:")
    print(sales_df.head())


if __name__ == "__main__":
    main()