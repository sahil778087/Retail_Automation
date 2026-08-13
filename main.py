import sys
from datetime import datetime

from Inventory_API.run_inventory import main as run_inventory
from Master_API.run_master import main as run_master
from Sales_API.run_sales import main as run_sales


def main():

    # -------------------------------------------------
    # Validate Sales Date
    # -------------------------------------------------

    if len(sys.argv) != 2:
        raise ValueError(
            "Usage: python main.py YYYY-MM-DD"
        )

    sales_date = sys.argv[1]

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
    # MASTER
    # -------------------------------------------------

    run_master()

    # -------------------------------------------------
    # INVENTORY
    # -------------------------------------------------

    run_inventory()

    # -------------------------------------------------
    # SALES
    # -------------------------------------------------

    run_sales(
        sales_date=sales_date
    )


if __name__ == "__main__":
    main()