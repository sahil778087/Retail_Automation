import sys
from datetime import datetime

from Inventory_API.run_inventory import main as run_inventory
from Master_API.run_master import main as run_master
from Sales_API.run_sales import main as run_sales


def main():

    if len(sys.argv) != 2:

        raise ValueError(
            "Usage: python main.py "
            "[inventory|sales|master]"
        )

    process = sys.argv[1].lower()

    # -------------------------------------------------
    # INVENTORY
    # -------------------------------------------------

    if process == "inventory":

        run_inventory()

    # -------------------------------------------------
    # SALES
    # -------------------------------------------------

    elif process == "sales":

        sales_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        run_sales(
            sales_date=sales_date
        )

    # -------------------------------------------------
    # MASTER
    # -------------------------------------------------

    elif process == "master":

        run_master()

    # -------------------------------------------------
    # INVALID PROCESS
    # -------------------------------------------------

    else:

        raise ValueError(
            f"Unknown process: {process}. "
            "Use inventory, sales, or master."
        )


if __name__ == "__main__":
    main()