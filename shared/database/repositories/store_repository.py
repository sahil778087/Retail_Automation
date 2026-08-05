def sync_stores(
    connection,
    stores_df
):
    """
    Synchronize stores into the store master table.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO store
        (
            store_id,
            store_name
        )
        VALUES
        (
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            store_name = VALUES(store_name),
            is_active = TRUE,
            updated_at = CURRENT_TIMESTAMP
    """

    rows = [
        (
            int(row.store_id),
            str(row.store_name)
        )
        for row in stores_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    affected_rows = cursor.rowcount

    cursor.close()

    return affected_rows