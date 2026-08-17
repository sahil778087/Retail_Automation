from decimal import Decimal

from shared.database.repositories.alert_repository import (
    get_alert_threshold,
    get_current_alert,
    create_inventory_alert,
    update_inventory_alert,
    resolve_inventory_alert,
    create_alert_history
)


# -------------------------------------------------
# Inventory State IDs
# -------------------------------------------------

STATE_HEALTHY = 1
STATE_CRITICAL = 2
STATE_ZERO = 3
STATE_NEGATIVE = 4


def evaluate_inventory_state(
    stock_quantity,
    threshold_quantity
):
    """
    Determine the current inventory state.

    Rules
    -----
    stock > threshold
        -> Healthy

    0 < stock <= threshold
        -> Critical

    stock == 0
        -> Zero

    stock < 0
        -> Negative
    """

    stock = Decimal(str(stock_quantity))
    threshold = Decimal(str(threshold_quantity))

    if stock < 0:
        return STATE_NEGATIVE

    if stock == 0:
        return STATE_ZERO

    if stock <= threshold:
        return STATE_CRITICAL

    return STATE_HEALTHY


def get_state_name(state_id):
    """
    Convert inventory state ID to state name.
    """

    state_names = {
        STATE_HEALTHY: "Healthy",
        STATE_CRITICAL: "Critical",
        STATE_ZERO: "Zero",
        STATE_NEGATIVE: "Negative"
    }

    return state_names.get(
        state_id,
        "Unknown"
    )


def process_inventory_alert(
    connection,
    run_id,
    store_id,
    product_id,
    stock_quantity
):
    """
    Evaluate inventory and manage the corresponding alert.

    Returns
    -------
    dict
        Result of the alert evaluation.
    """

    # -------------------------------------------------
    # Get Threshold
    # -------------------------------------------------

    threshold = get_alert_threshold(
        connection=connection,
        store_id=store_id,
        product_id=product_id
    )

    # No threshold means this product is not configured
    # for alert evaluation.
    if threshold is None:

        return {
            "status": "SKIPPED",
            "reason": "NO_THRESHOLD",
            "store_id": store_id,
            "product_id": product_id
        }

    threshold_quantity = threshold[
        "threshold_quantity"
    ]

    # -------------------------------------------------
    # Evaluate Current State
    # -------------------------------------------------

    current_state_id = evaluate_inventory_state(
        stock_quantity=stock_quantity,
        threshold_quantity=threshold_quantity
    )

    # -------------------------------------------------
    # Get Existing Alert
    # -------------------------------------------------

    current_alert = get_current_alert(
        connection=connection,
        store_id=store_id,
        product_id=product_id
    )

    # -------------------------------------------------
    # Determine Previous State
    # -------------------------------------------------

    previous_state_id = None

    if current_alert:

        previous_state_id = evaluate_inventory_state(
            stock_quantity=current_alert[
                "stock_quantity"
            ],
            threshold_quantity=current_alert[
                "threshold_quantity"
            ]
        )

    # -------------------------------------------------
    # HEALTHY
    # -------------------------------------------------

    if current_state_id == STATE_HEALTHY:

        if current_alert:

            resolve_inventory_alert(
                connection=connection,
                alert_id=current_alert["alert_id"],
                stock_quantity=stock_quantity,
                threshold_quantity=threshold_quantity
            )

            create_alert_history(
                connection=connection,
                run_id=run_id,
                store_id=store_id,
                product_id=product_id,
                previous_state_id=previous_state_id,
                current_state_id=current_state_id,
                alert_type="RESOLVED"
            )

            return {
                "status": "RESOLVED",
                "store_id": store_id,
                "product_id": product_id
            }

        return {
            "status": "HEALTHY",
            "store_id": store_id,
            "product_id": product_id
        }

    # -------------------------------------------------
    # ALERT STATE
    # -------------------------------------------------

    alert_type = get_state_name(
        current_state_id
    ).upper()

    # -------------------------------------------------
    # Existing OPEN Alert
    # -------------------------------------------------

    if current_alert:

        update_inventory_alert(
            connection=connection,
            alert_id=current_alert["alert_id"],
            stock_quantity=stock_quantity,
            threshold_quantity=threshold_quantity
        )

        create_alert_history(
            connection=connection,
            run_id=run_id,
            store_id=store_id,
            product_id=product_id,
            previous_state_id=previous_state_id,
            current_state_id=current_state_id,
            alert_type=alert_type
        )

        return {
            "status": "UPDATED",
            "alert_id": current_alert["alert_id"],
            "store_id": store_id,
            "product_id": product_id,
            "state": alert_type
        }

    # -------------------------------------------------
    # Create New Alert
    # -------------------------------------------------

    alert_id = create_inventory_alert(
        connection=connection,
        store_id=store_id,
        product_id=product_id,
        stock_quantity=stock_quantity,
        threshold_quantity=threshold_quantity
    )

    create_alert_history(
        connection=connection,
        run_id=run_id,
        store_id=store_id,
        product_id=product_id,
        previous_state_id=previous_state_id,
        current_state_id=current_state_id,
        alert_type=alert_type
    )

    return {
        "status": "CREATED",
        "alert_id": alert_id,
        "store_id": store_id,
        "product_id": product_id,
        "state": alert_type
    }



def process_inventory_alerts(
    connection,
    run_id,
    inventory_df,
    logger
):
    """
    Evaluate alerts for all inventory records
    in the current inventory snapshot.
    """

    results = {
        "CREATED": 0,
        "UPDATED": 0,
        "RESOLVED": 0,
        "HEALTHY": 0,
        "SKIPPED": 0
    }

    for row in inventory_df.itertuples(index=False):

        result = process_inventory_alert(
            connection=connection,
            run_id=run_id,
            store_id=int(row.store_id),
            product_id=int(row.product_id),
            stock_quantity=row.stock_quantity
        )

        status = result["status"]

        if status in results:
            results[status] += 1

        else:
            logger.warning(
                f"Unknown Alert Status : {status}"
            )

    logger.info(
        "Inventory Alert Evaluation Completed"
    )

    logger.info(
        f"Alerts Created  : {results['CREATED']}"
    )

    logger.info(
        f"Alerts Updated  : {results['UPDATED']}"
    )

    logger.info(
        f"Alerts Resolved : {results['RESOLVED']}"
    )

    logger.info(
        f"Healthy Products : {results['HEALTHY']}"
    )

    logger.info(
        f"Skipped Products : {results['SKIPPED']}"
    )

    return results