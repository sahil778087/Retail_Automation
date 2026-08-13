from shared.auth import get_partner_token
from shared.store_loader import load_stores
from shared.sales_parser import parse_sales

from shared.database.repositories.sales_repository import (
    get_sales_checkpoint,
    get_existing_product_ids
)

from Sales_API.qb_sales_api import fetch_sales
from shared.master_sync import ensure_products_exist


def get_order_serial(order_id: str) -> int:
    """
    Extract the final serial number from a QueueBuster Order ID.

    Example:
        OR12386720260101-894
        -> 894
    """

    try:
        return int(str(order_id).rsplit("-", 1)[-1])

    except (ValueError, IndexError):
        raise ValueError(
            f"Unable to extract order serial from Order ID: {order_id}"
        )


def filter_new_orders(
    orders,
    connection,
    sales_date,
    valid_store_ids
):
    """
    Keep only orders that are newer than the
    last successfully processed checkpoint for
    each store.

    Returns
    -------
    tuple
        (
            new_orders,
            checkpoint_updates
        )
    """

    new_orders = []

    checkpoint_updates = {}

    for order in orders:

        store_id = order.get("storeID")
        order_id = order.get("orderID")
        order_time = order.get("orderTime")

        if store_id is None:
            continue

        store_id = int(store_id)

        # Ignore stores that are not configured
        if store_id not in valid_store_ids:
            continue

        if not order_id:
            continue

        current_serial = get_order_serial(order_id)

        checkpoint = get_sales_checkpoint(
            connection=connection,
            store_id=store_id,
            sales_date=sales_date
        )

        if checkpoint:

            last_order_id = checkpoint["last_order_id"]

            last_serial = get_order_serial(
                last_order_id
            )

            if current_serial <= last_serial:
                continue

        new_orders.append(order)

        # Keep the latest order for checkpoint update
        existing = checkpoint_updates.get(store_id)

        if existing is None:

            checkpoint_updates[store_id] = (
                order_id,
                order_time
            )

        else:

            existing_serial = get_order_serial(
                existing[0]
            )

            if current_serial > existing_serial:

                checkpoint_updates[store_id] = (
                    order_id,
                    order_time
                )

    return new_orders, checkpoint_updates


def fetch_sales_for_date(
    sales_date: str,
    connection,
    logger
):
    """
    Fetch and prepare incremental sales
    for all configured stores for a date.
    """

    # -------------------------------------------------
    # Generate Partner Token
    # -------------------------------------------------

    auth = get_partner_token()

    token = auth["token"]

    logger.info(
        "Partner Token Generated"
    )

    # -------------------------------------------------
    # Load Stores
    # -------------------------------------------------

    stores = load_stores()

    logger.info(
        f"Loaded {len(stores)} Stores"
    )

    valid_store_ids = set(
        stores["store_id"].astype(int)
    )

    # -------------------------------------------------
    # Fetch Sales
    # -------------------------------------------------

    logger.info(
        f"Fetching Sales : {sales_date}"
    )

    response = fetch_sales(
        sales_date=sales_date,
        token=token
    )

    orders = response.get(
        "data",
        []
    )

    logger.info(
        f"Orders Retrieved : {len(orders):,}"
    )

    # -------------------------------------------------
    # Filter Incremental Orders
    # -------------------------------------------------

    new_orders, checkpoint_updates = filter_new_orders(
        orders=orders,
        connection=connection,
        sales_date=sales_date,
        valid_store_ids=valid_store_ids
    )

    logger.info(
        f"New Orders : {len(new_orders):,}"
    )

    # -------------------------------------------------
    # Parse New Orders
    # -------------------------------------------------

    incremental_response = {
        "status": True,
        "data": new_orders
    }

    sales_df = parse_sales(
        incremental_response
    )

    logger.info(
        f"Sales Rows Retrieved : {len(sales_df):,}"
    )

    # -------------------------------------------------
    # Recover Missing Product Master Data
    # -------------------------------------------------

    if not sales_df.empty:

        product_ids = (
            sales_df["product_id"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        # Negative QueueBuster beta product IDs
        # are not legitimate master products.
        valid_product_ids = [
            product_id
            for product_id in product_ids
            if product_id > 0
        ]

        if valid_product_ids:

            existing_product_ids = get_existing_product_ids(
                connection=connection,
                product_ids=valid_product_ids
            )

            missing_product_ids = [
                product_id
                for product_id in valid_product_ids
                if product_id not in existing_product_ids
            ]

            if missing_product_ids:

                logger.info(
                    f"Missing Sales Products : "
                    f"{missing_product_ids}"
                )

                ensure_products_exist(
                    connection=connection,
                    product_ids=missing_product_ids,
                    token=token,
                    logger=logger
                )

    return sales_df, checkpoint_updates