def sync_categories(connection, inventory_df):

    cursor = connection.cursor()

    query = """
        INSERT INTO category
        (
            category_id,
            category_name
        )
        VALUES
        (
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            category_name = VALUES(category_name),
            updated_at = CURRENT_TIMESTAMP
    """

    categories = (
        inventory_df[
            [
                "category_id",
                "category_name"
            ]
        ]
        .drop_duplicates()
        .sort_values("category_id")
    )

    rows = [
        (
            int(row.category_id),
            str(row.category_name)
        )
        for row in categories.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    cursor.close()