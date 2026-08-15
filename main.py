import sys
from datetime import datetime

from Inventory_API.run_inventory import main as run_inventory
from Master_API.run_master import main as run_master
from Sales_API.run_sales import main as run_sales


def main():

    # -------------------------------------------------
    # ARGUMENT VALIDATION
    # -------------------------------------------------

    if len(sys.argv) < 2 or len(sys.argv) > 3:

        raise ValueError(
            "Usage: python main.py "
            "[inventory|sales|master] "
            "[YYYY-MM-DD]"
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

        # If date is provided → use it
        if len(sys.argv) == 3:

            sales_date = sys.argv[2]

            # Validate date format
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

        # Otherwise → today's date
        else:

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