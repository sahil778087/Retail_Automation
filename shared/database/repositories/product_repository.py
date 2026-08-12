import pandas as pd

def sync_products(connection, product_df):

    if product_df.empty:
        return 0

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

    rows = [
        (
            int(row.product_id),
            str(row.product_name),
            int(row.category_id) if not pd.isna(row.category_id) else None,
            int(row.sub_category_id) if not pd.isna(row.sub_category_id) else None,
            int(row.brand_id) if not pd.isna(row.brand_id) else None,
            None if not row.barcode else str(row.barcode),
            str(row.unit)
        )
        for row in product_df.itertuples(index=False)
    ]

    cursor.executemany(query, rows)

    rows_affected = cursor.rowcount

    cursor.close()

    return rows_affected