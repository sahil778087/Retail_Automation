def get_store_name(
    connection,
    store_id
):
    """
    Get store name from the store master.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT store_name
        FROM store
        WHERE store_id = %s
          AND is_active = 1
        LIMIT 1
    """

    cursor.execute(
        query,
        (store_id,)
    )

    row = cursor.fetchone()

    cursor.close()

    if row:
        return row["store_name"]

    return str(store_id)


def get_product_details(
    connection,
    product_id
):
    """
    Get product information from the product master.
    """

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            product_name,
            unit
        FROM product
        WHERE product_id = %s
          AND is_active = 1
        LIMIT 1
    """

    cursor.execute(
        query,
        (product_id,)
    )

    row = cursor.fetchone()

    cursor.close()

    if row:
        return row

    return {
        "product_name": str(product_id),
        "unit": None
    }