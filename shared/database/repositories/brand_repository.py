def sync_brands(connection, brand_df):

    if brand_df.empty:
        return 0

    cursor = connection.cursor()

    query = """
        INSERT INTO brand
        (
            brand_id,
            brand_name,
            is_active
        )
        VALUES
        (
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            brand_name = VALUES(brand_name),
            is_active = VALUES(is_active),
            updated_at = CURRENT_TIMESTAMP
    """

    rows = [
        (
            int(row.brand_id),
            str(row.brand_name),
            int(row.is_active)
        )
        for row in brand_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected