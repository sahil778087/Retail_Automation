def sync_brands(connection, inventory_df):

    cursor = connection.cursor()

    query = """
        INSERT INTO brand
        (
            brand_id,
            brand_name
        )
        VALUES
        (
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            brand_name = VALUES(brand_name),
            updated_at = CURRENT_TIMESTAMP
    """

    brands = (
        inventory_df[
            [
                "brand_id",
                "brand_name"
            ]
        ]
        .drop_duplicates()
        .sort_values("brand_id")
    )

    rows = [
        (
            int(row.brand_id),
            str(row.brand_name)
        )
        for row in brands.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    cursor.close()