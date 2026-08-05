def bulk_insert_inventory(
    connection,
    inventory_df,
    run_id
):
    """
    Bulk insert inventory snapshots.
    """

    cursor = connection.cursor()

    query = """
        INSERT INTO inventory_snapshot
        (
            run_id,
            store_id,
            product_id,
            stock_quantity
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    rows = [
        (
            run_id,
            int(row.store_id),
            int(row.product_id),
            float(row.stock_quantity)
        )
        for row in inventory_df.itertuples(index=False)
    ]

    cursor.executemany(
        query,
        rows
    )

    inserted_rows = cursor.rowcount

    cursor.close()

    return inserted_rows