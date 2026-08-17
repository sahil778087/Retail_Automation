def get_alert_threshold(
    connection,
    store_id,
    product_id
):
    """
    Get the active alert threshold
    for a store-product combination.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            threshold_id,
            store_id,
            product_id,
            threshold_quantity,
            threshold_type
        FROM alert_threshold
        WHERE store_id = %s
          AND product_id = %s
          AND is_active = 1
    """

    cursor.execute(
        query,
        (
            store_id,
            product_id
        )
    )

    result = cursor.fetchone()

    cursor.close()

    return result

def get_alert_thresholds(
    connection
):
    """
    Get all active alert thresholds.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            store_id,
            product_id,
            threshold_quantity,
            threshold_type
        FROM alert_threshold
        WHERE is_active = 1
    """

    cursor.execute(query)

    results = cursor.fetchall()

    cursor.close()

    return results



def upsert_alert_threshold(
    connection,
    store_id,
    product_id,
    threshold_quantity,
    threshold_type="MEAN_7D"
):
    """
    Create or update the threshold for a
    store-product combination.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO alert_threshold
        (
            store_id,
            product_id,
            threshold_quantity,
            threshold_type,
            is_active
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            1
        )

        ON DUPLICATE KEY UPDATE

            threshold_quantity = VALUES(threshold_quantity),
            threshold_type = VALUES(threshold_type),
            is_active = 1,
            updated_at = CURRENT_TIMESTAMP
    """

    cursor.execute(
        query,
        (
            store_id,
            product_id,
            threshold_quantity,
            threshold_type
        )
    )

    affected_rows = cursor.rowcount

    cursor.close()

    return affected_rows



def get_current_alert(
    connection,
    store_id,
    product_id
):
    """
    Get the currently open inventory alert
    for a store-product combination.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            alert_id,
            store_id,
            product_id,
            stock_quantity,
            threshold_quantity,
            alert_status,
            first_detected_at,
            last_detected_at,
            resolved_at
        FROM inventory_alert
        WHERE store_id = %s
          AND product_id = %s
          AND alert_status = 'OPEN'
        ORDER BY alert_id DESC
        LIMIT 1
    """

    cursor.execute(
        query,
        (
            store_id,
            product_id
        )
    )

    result = cursor.fetchone()

    cursor.close()

    return result



def create_inventory_alert(
    connection,
    store_id,
    product_id,
    stock_quantity,
    threshold_quantity
):
    """
    Create a new open inventory alert.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO inventory_alert
        (
            store_id,
            product_id,
            stock_quantity,
            threshold_quantity,
            alert_status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            'OPEN'
        )
    """

    cursor.execute(
        query,
        (
            store_id,
            product_id,
            stock_quantity,
            threshold_quantity
        )
    )

    alert_id = cursor.lastrowid

    cursor.close()

    return alert_id


def update_inventory_alert(
    connection,
    alert_id,
    stock_quantity,
    threshold_quantity
):
    """
    Update an existing open inventory alert.
    """

    cursor = connection.cursor()

    query = """
        UPDATE inventory_alert
        SET
            stock_quantity = %s,
            threshold_quantity = %s,
            last_detected_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE alert_id = %s
          AND alert_status = 'OPEN'
    """

    cursor.execute(
        query,
        (
            stock_quantity,
            threshold_quantity,
            alert_id
        )
    )

    affected_rows = cursor.rowcount

    cursor.close()

    return affected_rows



def create_alert_history(
    connection,
    run_id,
    store_id,
    product_id,
    previous_state_id,
    current_state_id,
    alert_type
):
    """
    Record an inventory state evaluation in alert_history.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO alert_history
        (
            run_id,
            store_id,
            product_id,
            previous_state_id,
            current_state_id,
            alert_type
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.execute(
        query,
        (
            run_id,
            store_id,
            product_id,
            previous_state_id,
            current_state_id,
            alert_type
        )
    )

    alert_id = cursor.lastrowid

    cursor.close()

    return alert_id


def resolve_inventory_alert(
    connection,
    alert_id,
    stock_quantity,
    threshold_quantity
):
    """
    Resolve an existing inventory alert.
    """

    cursor = connection.cursor()

    query = """
        UPDATE inventory_alert
        SET
            stock_quantity = %s,
            threshold_quantity = %s,
            alert_status = 'RESOLVED',
            resolved_at = CURRENT_TIMESTAMP,
            last_detected_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE alert_id = %s
    """

    cursor.execute(
        query,
        (
            stock_quantity,
            threshold_quantity,
            alert_id
        )
    )

    affected_rows = cursor.rowcount

    cursor.close()

    return affected_rows



