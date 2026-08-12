def sync_sub_categories(connection, sub_categories_df):

    if sub_categories_df.empty:
        return 0

    cursor = connection.cursor()

    query = """
        INSERT INTO sub_category
        (
            sub_category_id,
            subcategory_name,
            category_id
        )
        VALUES
        (
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            subcategory_name = VALUES(subcategory_name),
            category_id = VALUES(category_id),
            updated_at = CURRENT_TIMESTAMP
    """

    rows = [
        (
            int(row.sub_category_id),
            str(row.sub_category_name),
            int(row.category_id)
        )
        for row in sub_categories_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected