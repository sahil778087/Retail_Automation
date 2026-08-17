from datetime import date, timedelta

from shared.database.repositories.alert_repository import (
    upsert_alert_threshold
)


def get_7_day_demand(
    connection,
    store_id,
    product_id,
    reference_date
):
    """
    Calculate average daily sales quantity
    for a store-product over the previous 7 calendar days.

    The reference date is NOT included.

    Example:
        reference_date = 2026-08-16

        Demand window:
            2026-08-09
            through
            2026-08-15
    """

    start_date = reference_date - timedelta(days=7)

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            COALESCE(
                SUM(quantity),
                0
            ) AS total_quantity
        FROM sales_fact
        WHERE store_id = %s
          AND product_id = %s
          AND order_time >= %s
          AND order_time < %s
    """

    cursor.execute(
        query,
        (
            store_id,
            product_id,
            start_date,
            reference_date
        )
    )

    result = cursor.fetchone()

    cursor.close()

    total_quantity = result["total_quantity"] or 0

    average_daily_demand = (
        float(total_quantity) / 7
    )

    return average_daily_demand


def get_active_store_products(
    connection,
    reference_date
):
    """
    Get distinct store-product combinations
    that have sales history before the reference date.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT DISTINCT
            store_id,
            product_id
        FROM sales_fact
        WHERE order_time < %s
        ORDER BY
            store_id,
            product_id
    """

    cursor.execute(
        query,
        (reference_date,)
    )

    rows = cursor.fetchall()

    cursor.close()

    return rows


def calculate_7_day_thresholds(
    connection,
    reference_date
):
    """
    Calculate 7-day average demand for every
    active store-product combination.

    Returns
    -------
    list of dict
    """

    store_products = get_active_store_products(
        connection=connection,
        reference_date=reference_date
    )

    thresholds = []

    for row in store_products:

        store_id = int(row["store_id"])
        product_id = int(row["product_id"])

        average_daily_demand = round(
            get_7_day_demand(
                connection=connection,
                store_id=store_id,
                product_id=product_id,
                reference_date=reference_date
            ),
            2
        )

        thresholds.append(
            {
                "store_id": store_id,
                "product_id": product_id,
                "threshold_quantity": average_daily_demand,
                "threshold_type": "MEAN_7D"
            }
        )

    return thresholds


def save_7_day_thresholds(
    connection,
    reference_date
):
    """
    Calculate 7-day demand thresholds and save them
    into alert_threshold.
    """

    thresholds = calculate_7_day_thresholds(
        connection=connection,
        reference_date=reference_date
    )

    updated_rows = 0

    for threshold in thresholds:

        updated_rows += upsert_alert_threshold(
            connection=connection,
            store_id=threshold["store_id"],
            product_id=threshold["product_id"],
            threshold_quantity=threshold["threshold_quantity"],
            threshold_type=threshold["threshold_type"]
        )

    return {
        "thresholds": thresholds,
        "updated_rows": updated_rows
    }