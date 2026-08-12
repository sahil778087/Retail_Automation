import pandas as pd


FINAL_COLUMNS = [
    "order_sub_id",
    "order_id",
    "invoice_no",
    "store_id",
    "product_id",
    "quantity",
    "selling_price",
    "mrp",
    "sales_amount",
    "order_time"
]


def parse_sales(response: dict) -> pd.DataFrame:
    """
    Convert QueueBuster Sales API response
    into sales_fact format.
    """

    if not response.get("status", False):
        raise ValueError(
            "QueueBuster Sales API returned an unsuccessful response."
        )

    orders = response.get("data", [])

    if not orders:
        return pd.DataFrame(columns=FINAL_COLUMNS)

    rows = []

    for order in orders:

        order_id = order.get("orderID")
        invoice_no = order.get("invoiceNumber")
        store_id = order.get("storeID")
        order_time = order.get("orderTime")

        for item in order.get("itemDetails", []):

            rows.append(
                {
                    "order_sub_id": item.get("orderSubID"),
                    "order_id": order_id,
                    "invoice_no": invoice_no,
                    "store_id": store_id,
                    "product_id": item.get("productID"),
                    "quantity": item.get("quantity"),
                    "selling_price": item.get("rate"),
                    "mrp": item.get("MRP"),
                    "sales_amount": item.get("itemSales"),
                    "order_time": order_time
                }
            )

    if not rows:
        return pd.DataFrame(columns=FINAL_COLUMNS)

    df = pd.DataFrame(rows)

    df = df[FINAL_COLUMNS]

    return df