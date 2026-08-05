def sync_sub_categories(connection, inventory_df):

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

    sub_categories = (
        inventory_df[
            [
                "sub_category_id",
                "sub_category_name",
                "category_id"
            ]
        ]
        .drop_duplicates()
        .sort_values("sub_category_id")
    )

    rows = [
        (
            int(row.sub_category_id),
            str(row.sub_category_name),
            int(row.category_id)
        )
        for row in sub_categories.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    cursor.close()