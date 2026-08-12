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
            %s
        )

        ON DUPLICATE KEY UPDATE

            quantity = VALUES(quantity),
            selling_price = VALUES(selling_price),
            mrp = VALUES(mrp),
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