def sync_categories(connection, category_df):

    if category_df.empty:
        return 0

    cursor = connection.cursor()

    query = """
        INSERT INTO category
        (
            category_id,
            category_name,
            is_active
        )
        VALUES
        (
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            category_name = VALUES(category_name),
            is_active = VALUES(is_active),
            updated_at = CURRENT_TIMESTAMP
    """

    rows = [
        (
            int(row.category_id),
            str(row.category_name),
            int(row.is_active)
        )
        for row in category_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected