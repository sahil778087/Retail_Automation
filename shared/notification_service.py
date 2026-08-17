from shared.telegram_service import send_telegram_message

from shared.database.repositories.notification_repository import (
    create_notification,
    mark_notification_sent,
    mark_notification_failed
)


def send_inventory_alert_notification(
    connection,
    alert_id,
    store_name,
    store_id,
    product_name,
    product_id,
    stock_quantity,
    threshold_quantity
):
    """
    Send notification for a newly created inventory alert
    and record notification history.
    """

    message = (
        "🚨 INVENTORY ALERT\n\n"
        f"🏪 Store: {store_name}\n"
        f"Store ID: {store_id}\n\n"
        f"📦 Product: {product_name}\n"
        f"Product ID: {product_id}\n\n"
        f"📊 Current Stock: {stock_quantity}\n"
        f"⚠️ Threshold: {threshold_quantity}\n\n"
        "🔴 Status: OPEN"
    )

    # -------------------------------------------------
    # Create Pending Notification
    # -------------------------------------------------

    notification_id = create_notification(
        connection=connection,
        alert_id=alert_id,
        channel="TELEGRAM"
    )

    try:

        # -------------------------------------------------
        # Send Telegram Message
        # -------------------------------------------------

        telegram_result = send_telegram_message(
            message
        )

        message_id = (
            telegram_result
            .get("result", {})
            .get("message_id")
        )

        # -------------------------------------------------
        # Mark Notification as SENT
        # -------------------------------------------------

        mark_notification_sent(
            connection=connection,
            notification_id=notification_id,
            message_id=message_id
        )

        return telegram_result

    except Exception as notification_error:

        # -------------------------------------------------
        # Mark Notification as FAILED
        # -------------------------------------------------

        mark_notification_failed(
            connection=connection,
            notification_id=notification_id,
            error_message=str(notification_error)
        )

        raise


def send_inventory_resolved_notification(
    connection,
    alert_id,
    store_name,
    store_id,
    product_name,
    product_id,
    stock_quantity,
    threshold_quantity
):
    """
    Send notification when an inventory alert is resolved
    and record notification history.
    """

    message = (
        "✅ INVENTORY ALERT RESOLVED\n\n"
        f"🏪 Store: {store_name}\n"
        f"Store ID: {store_id}\n\n"
        f"📦 Product: {product_name}\n"
        f"Product ID: {product_id}\n\n"
        f"📊 Current Stock: {stock_quantity}\n"
        f"⚠️ Previous Threshold: {threshold_quantity}\n\n"
        "🟢 Status: RESOLVED"
    )

    # -------------------------------------------------
    # Create Pending Notification
    # -------------------------------------------------

    notification_id = create_notification(
        connection=connection,
        alert_id=alert_id,
        channel="TELEGRAM"
    )

    try:

        # -------------------------------------------------
        # Send Telegram Message
        # -------------------------------------------------

        telegram_result = send_telegram_message(
            message
        )

        message_id = (
            telegram_result
            .get("result", {})
            .get("message_id")
        )

        # -------------------------------------------------
        # Mark Notification as SENT
        # -------------------------------------------------

        mark_notification_sent(
            connection=connection,
            notification_id=notification_id,
            message_id=message_id
        )

        return telegram_result

    except Exception as notification_error:

        # -------------------------------------------------
        # Mark Notification as FAILED
        # -------------------------------------------------

        mark_notification_failed(
            connection=connection,
            notification_id=notification_id,
            error_message=str(notification_error)
        )

        raise