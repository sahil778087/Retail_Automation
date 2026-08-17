from shared.alert_evaluator import (
    STATE_HEALTHY,
    STATE_CRITICAL,
    STATE_ZERO,
    STATE_NEGATIVE,
    evaluate_inventory_state
)

from shared.database.repositories.alert_repository import (
    get_current_alert,
    create_inventory_alert,
    resolve_inventory_alert,
    update_inventory_alert,
    create_alert_history
)

from shared.notification_service import (
    send_inventory_alert_notification,
    send_inventory_resolved_notification
)

from shared.database.repositories.master_repository import (
    get_store_name,
    get_product_details
)

# -------------------------------------------------
# Alertable States
# -------------------------------------------------

ALERT_STATES = {
    STATE_CRITICAL,
    STATE_NEGATIVE
}


def process_inventory_alert(
    connection,
    run_id,
    store_id,
    product_id,
    stock_quantity,
    threshold_quantity,
    logger
):
    """
    Evaluate inventory and maintain the current
    inventory alert lifecycle.

    Returns
    -------
    dict
        Result of the alert evaluation.
    """

    # -------------------------------------------------
    # Evaluate Current Inventory State
    # -------------------------------------------------

    current_state = evaluate_inventory_state(
        stock_quantity=stock_quantity,
        threshold_quantity=threshold_quantity
    )

    # -------------------------------------------------
    # Get Existing Open Alert
    # -------------------------------------------------

    existing_alert = get_current_alert(
        connection=connection,
        store_id=store_id,
        product_id=product_id
    )

    previous_state = None

    if existing_alert:

        previous_state = evaluate_inventory_state(
            stock_quantity=existing_alert["stock_quantity"],
            threshold_quantity=existing_alert["threshold_quantity"]
        )

    # -------------------------------------------------
    # Healthy
    # -------------------------------------------------

    if current_state == STATE_HEALTHY:

        if existing_alert:

            resolve_inventory_alert(
                connection=connection,
                alert_id=existing_alert["alert_id"],
                stock_quantity=stock_quantity,
                threshold_quantity=threshold_quantity
            )

            create_alert_history(
                connection=connection,
                run_id=run_id,
                store_id=store_id,
                product_id=product_id,
                previous_state_id=previous_state,
                current_state_id=current_state,
                alert_type="RESOLVED"
            )

            logger.info(
                f"Alert Resolved | "
                f"Store={store_id} | "
                f"Product={product_id} | "
                f"Stock={stock_quantity}"
            )

            # -------------------------------------------------
            # Fetch Store and Product Details
            # -------------------------------------------------

            store_name = get_store_name(
                connection=connection,
                store_id=store_id
            )

            product_details = get_product_details(
                connection=connection,
                product_id=product_id
            )

            product_name = product_details["product_name"]

            # -------------------------------------------------
            # Telegram - Alert Resolved
            # -------------------------------------------------

            send_inventory_resolved_notification(
                connection=connection,
                alert_id=existing_alert["alert_id"],
                store_name=store_name,
                store_id=store_id,
                product_name=product_name,
                product_id=product_id,
                stock_quantity=stock_quantity,
                threshold_quantity=threshold_quantity
            )

            return {
                "action": "RESOLVED",
                "state_id": current_state,
                "alert_id": existing_alert["alert_id"]
            }

        return {
            "action": "NONE",
            "state_id": current_state,
            "alert_id": None
        }

    # -------------------------------------------------
    # Zero
    # -------------------------------------------------

    if current_state == STATE_ZERO:

        # Zero stock does not create a new alert
        # because zero can occur during inventory audits.

        if existing_alert:

            update_inventory_alert(
                connection=connection,
                alert_id=existing_alert["alert_id"],
                stock_quantity=stock_quantity,
                threshold_quantity=threshold_quantity
            )

            create_alert_history(
                connection=connection,
                run_id=run_id,
                store_id=store_id,
                product_id=product_id,
                previous_state_id=previous_state,
                current_state_id=current_state,
                alert_type="KEEP_OPEN"
            )

            logger.info(
                f"Zero Stock | Existing Alert Kept Open | "
                f"Store={store_id} | "
                f"Product={product_id}"
            )

            return {
                "action": "KEEP_OPEN",
                "state_id": current_state,
                "alert_id": existing_alert["alert_id"]
            }

        return {
            "action": "NONE",
            "state_id": current_state,
            "alert_id": None
        }

    # -------------------------------------------------
    # Critical / Negative
    # -------------------------------------------------

    if current_state in ALERT_STATES:

        # -------------------------------------------------
        # Existing Alert
        # -------------------------------------------------

        if existing_alert:

            update_inventory_alert(
                connection=connection,
                alert_id=existing_alert["alert_id"],
                stock_quantity=stock_quantity,
                threshold_quantity=threshold_quantity
            )

            create_alert_history(
                connection=connection,
                run_id=run_id,
                store_id=store_id,
                product_id=product_id,
                previous_state_id=previous_state,
                current_state_id=current_state,
                alert_type="KEEP_OPEN"
            )

            logger.info(
                f"Alert Already Open | "
                f"Store={store_id} | "
                f"Product={product_id}"
            )

            return {
                "action": "KEEP_OPEN",
                "state_id": current_state,
                "alert_id": existing_alert["alert_id"]
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
            previous_state_id=previous_state,
            current_state_id=current_state,
            alert_type="CREATED"
        )

        logger.warning(
            f"Inventory Alert Created | "
            f"Store={store_id} | "
            f"Product={product_id} | "
            f"Stock={stock_quantity} | "
            f"Threshold={threshold_quantity}"
        )

        # -------------------------------------------------
        # Fetch Store and Product Details
        # -------------------------------------------------

        store_name = get_store_name(
            connection=connection,
            store_id=store_id
        )

        product_details = get_product_details(
            connection=connection,
            product_id=product_id
        )

        product_name = product_details["product_name"]

        # -------------------------------------------------
        # Telegram - New Alert
        # -------------------------------------------------

        send_inventory_alert_notification(
            connection=connection,
            alert_id=alert_id,
            store_name=store_name,
            store_id=store_id,
            product_name=product_name,
            product_id=product_id,
            stock_quantity=stock_quantity,
            threshold_quantity=threshold_quantity
        )

        return {
            "action": "CREATED",
            "state_id": current_state,
            "alert_id": alert_id
        }

    # -------------------------------------------------
    # Fallback
    # -------------------------------------------------

    logger.warning(
        f"Unhandled Inventory State | "
        f"Store={store_id} | "
        f"Product={product_id} | "
        f"State={current_state}"
    )

    return {
        "action": "NONE",
        "state_id": current_state,
        "alert_id": None
    }