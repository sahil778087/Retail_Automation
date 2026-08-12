def sync_product_barcodes(connection, barcode_df):

    if barcode_df.empty:
        return 0

    cursor = connection.cursor()

    query = """
        INSERT INTO product_barcode
        (
            product_id,
            barcode,
            is_primary
        )
        VALUES
        (
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            is_primary = VALUES(is_primary)
    """

    rows = []

    for product_id, group in barcode_df.groupby("product_id"):

        for index, barcode in enumerate(group["barcode"]):

            rows.append(
                (
                    int(product_id),
                    str(barcode),
                    1 if index == 0 else 0
                )
            )

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected