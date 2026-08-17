from datetime import datetime


STATUS_PENDING = 1
STATUS_SENT = 2
STATUS_FAILED = 3
STATUS_RETRYING = 4


def create_notification(
    connection,
    alert_id,
    channel
):
    """
    Create a notification history record
    in PENDING state.

    Returns
    -------
    int
        notification_id
    """

    query = """
        INSERT INTO notification_history (
            alert_id,
            channel,
            status_id
        )
        VALUES (%s, %s, %s)
    """

    cursor = connection.cursor()

    try:

        cursor.execute(
            query,
            (
                alert_id,
                channel,
                STATUS_PENDING
            )
        )

        return cursor.lastrowid

    finally:

        cursor.close()


def mark_notification_sent(
    connection,
    notification_id,
    message_id
):
    """
    Mark notification as successfully sent.
    """

    query = """
        UPDATE notification_history
        SET
            status_id = %s,
            sent_at = %s,
            message_id = %s,
            error_message = NULL
        WHERE notification_id = %s
    """

    cursor = connection.cursor()

    try:

        cursor.execute(
            query,
            (
                STATUS_SENT,
                datetime.now(),
                str(message_id) if message_id is not None else None,
                notification_id
            )
        )

    finally:

        cursor.close()


def mark_notification_failed(
    connection,
    notification_id,
    error_message
):
    """
    Mark notification as failed.
    """

    query = """
        UPDATE notification_history
        SET
            status_id = %s,
            error_message = %s
        WHERE notification_id = %s
    """

    cursor = connection.cursor()

    try:

        cursor.execute(
            query,
            (
                STATUS_FAILED,
                str(error_message)[:500],
                notification_id
            )
        )

    finally:

        cursor.close()