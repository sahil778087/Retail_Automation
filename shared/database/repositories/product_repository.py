def sync_products(connection, inventory_df):

    cursor = connection.cursor()

    query = """
        INSERT INTO product
        (
            product_id,
            product_name,
            category_id,
            sub_category_id,
            brand_id,
            barcode,
            unit
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )

        ON DUPLICATE KEY UPDATE

            product_name = VALUES(product_name),
            category_id = VALUES(category_id),
            sub_category_id = VALUES(sub_category_id),
            brand_id = VALUES(brand_id),
            barcode = VALUES(barcode),
            unit = VALUES(unit),
            updated_at = CURRENT_TIMESTAMP
    """

    products = (
        inventory_df[
            [
                "product_id",
                "product_name",
                "category_id",
                "sub_category_id",
                "brand_id",
                "barcode",
                "unit"
            ]
        ]
        .drop_duplicates()
        .sort_values("product_id")
    )

    rows = [
        (
            int(row.product_id),
            str(row.product_name),
            int(row.category_id),
            int(row.sub_category_id),
            int(row.brand_id),
            None if not row.barcode else str(row.barcode),
            str(row.unit)
        )
        for row in products.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    cursor.close()