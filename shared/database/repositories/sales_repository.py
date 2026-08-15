def bulk_insert_sales(
    connection,
    sales_df
):
    """
    Bulk insert sales into sales_fact.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO sales_fact
        (
            order_id,
            order_sub_id,
            invoice_no,
            store_id,
            product_id,
            quantity,
            selling_price,
            mrp,
            discount_amount,
            sales_amount,
            order_time
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            quantity = VALUES(quantity),
            selling_price = VALUES(selling_price),
            mrp = VALUES(mrp),
            discount_amount = VALUES(discount_amount),
            sales_amount = VALUES(sales_amount),
            order_time = VALUES(order_time)
    """

    rows = [
        (
            str(row.order_id),
            int(row.order_sub_id),
            str(row.invoice_no),
            int(row.store_id),
            int(row.product_id),
            float(row.quantity),
            float(row.selling_price),
            float(row.mrp),
            float(row.discount_amount),
            float(row.sales_amount),
            row.order_time
        )
        for row in sales_df.itertuples(index=False)
    ]

    if not rows:
        cursor.close()
        return 0

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected


def bulk_insert_sales_orders(
    connection,
    order_df
):
    """
    Bulk insert bill-level sales into sales_order.
    """

    if order_df.empty:
        return 0

    cursor = connection.cursor()

    query = """
        INSERT INTO sales_order
        (
            order_id,
            invoice_no,
            store_id,
            order_time,
            gross_bill,
            total_item_sales,
            total_discount_amount,
            total_tax_amount,
            rounding,
            transaction_value,
            sales_value,
            total_item_count,
            total_item_quantity,
            payment_status,
            transaction_type
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE

            invoice_no = VALUES(invoice_no),
            store_id = VALUES(store_id),
            order_time = VALUES(order_time),
            gross_bill = VALUES(gross_bill),
            total_item_sales = VALUES(total_item_sales),
            total_discount_amount = VALUES(total_discount_amount),
            total_tax_amount = VALUES(total_tax_amount),
            rounding = VALUES(rounding),
            transaction_value = VALUES(transaction_value),
            sales_value = VALUES(sales_value),
            total_item_count = VALUES(total_item_count),
            total_item_quantity = VALUES(total_item_quantity),
            payment_status = VALUES(payment_status),
            transaction_type = VALUES(transaction_type),
            updated_at = CURRENT_TIMESTAMP
    """

    rows = [
        (
            str(row.order_id),
            str(row.invoice_no) if row.invoice_no else None,
            int(row.store_id),
            row.order_time,
            float(row.gross_bill),
            float(row.total_item_sales),
            float(row.total_discount_amount),
            float(row.total_tax_amount),
            float(row.rounding),
            float(row.transaction_value),
            float(row.sales_value),
            int(row.total_item_count),
            float(row.total_item_quantity),
            str(row.payment_status)
                if row.payment_status else None,
            str(row.transaction_type)
                if row.transaction_type else None
        )
        for row in order_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected



def bulk_insert_sales_payments(
    connection,
    payment_df
):
    """
    Insert payment-level sales into sales_payment.

    Existing payments for the affected orders are removed first.
    This makes retries and historical backfills safe.
    """

    if payment_df.empty:
        return 0

    cursor = connection.cursor()

    # -------------------------------------------------
    # Get affected orders
    # -------------------------------------------------

    order_ids = (
        payment_df["order_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not order_ids:
        cursor.close()
        return 0

    # -------------------------------------------------
    # Remove existing payments for these orders
    # -------------------------------------------------

    placeholders = ",".join(
        ["%s"] * len(order_ids)
    )

    delete_query = f"""
        DELETE FROM sales_payment
        WHERE order_id IN ({placeholders})
    """

    cursor.execute(
        delete_query,
        tuple(order_ids)
    )

    # -------------------------------------------------
    # Insert current payment data
    # -------------------------------------------------

    insert_query = """
        INSERT INTO sales_payment
        (
            order_id,
            payment_type,
            payment_sub_type,
            payment_amount,
            transaction_id,
            last_four_digit,
            reference_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    rows = [
        (
            str(row.order_id),
            row.payment_type,
            row.payment_sub_type,
            float(row.payment_amount or 0),
            row.transaction_id,
            row.last_four_digit,
            row.reference_id
        )
        for row in payment_df.itertuples(index=False)
    ]

    cursor.executemany(
        insert_query,
        rows
    )

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected





def get_existing_product_ids(
    connection,
    product_ids
):
    """
    Return product IDs that exist in the product master.
    """

    if not product_ids:
        return set()

    cursor = connection.cursor()

    placeholders = ",".join(
        ["%s"] * len(product_ids)
    )

    query = f"""
        SELECT product_id
        FROM product
        WHERE product_id IN ({placeholders})
    """

    cursor.execute(
        query,
        tuple(product_ids)
    )

    existing_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

    cursor.close()

    return existing_ids



def get_sales_checkpoint(
    connection,
    store_id,
    sales_date
):
    """
    Get the last successfully processed order
    for a store and sales date.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            store_id,
            sales_date,
            last_order_id,
            last_order_time
        FROM sales_checkpoint
        WHERE store_id = %s
          AND sales_date = %s
    """

    cursor.execute(
        query,
        (store_id, sales_date)
    )

    checkpoint = cursor.fetchone()

    cursor.close()

    return checkpoint


def update_sales_checkpoint(
    connection,
    store_id,
    sales_date,
    last_order_id,
    last_order_time
):
    """
    Create or update the sales checkpoint.

    This function does NOT commit.
    The caller controls the transaction.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO sales_checkpoint
        (
            store_id,
            sales_date,
            last_order_id,
            last_order_time
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            last_order_id = VALUES(last_order_id),
            last_order_time = VALUES(last_order_time),
            updated_at = CURRENT_TIMESTAMP
    """

    cursor.execute(
        query,
        (
            store_id,
            sales_date,
            last_order_id,
            last_order_time
        )
    )

    cursor.close()