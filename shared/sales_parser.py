import pandas as pd


# ============================================================
# SALES FACT — ITEM LEVEL
# ============================================================

FINAL_COLUMNS = [
    "order_sub_id",
    "order_id",
    "invoice_no",
    "store_id",
    "product_id",
    "quantity",
    "selling_price",
    "mrp",
    "discount_amount",
    "tax_amount",
    "sales_amount",
    "order_time"
]


# ============================================================
# SALES ORDER — BILL LEVEL
# ============================================================

ORDER_COLUMNS = [
    "order_id",
    "invoice_no",
    "store_id",
    "order_time",
    "gross_bill",
    "total_item_sales",
    "total_discount_amount",
    "total_tax_amount",
    "rounding",
    "transaction_value",
    "sales_value",
    "total_item_count",
    "total_item_quantity",
    "payment_status",
    "transaction_type"
]


# ============================================================
# SALES PAYMENT — PAYMENT LEVEL
# ============================================================

PAYMENT_COLUMNS = [
    "order_id",
    "payment_type",
    "payment_sub_type",
    "payment_amount",
    "transaction_id",
    "last_four_digit",
    "reference_id"
]


def parse_sales(response: dict):
    """
    Convert QueueBuster Sales API response into:

    1. sales_fact     -> item-level data
    2. sales_order    -> bill-level data
    3. sales_payment  -> payment-level data
    """

    # --------------------------------------------------------
    # Validate API Response
    # --------------------------------------------------------

    if not response.get("status", False):
        raise ValueError(
            "QueueBuster Sales API returned an unsuccessful response."
        )

    orders = response.get("data", [])

    if not orders:
        return (
            pd.DataFrame(columns=FINAL_COLUMNS),
            pd.DataFrame(columns=ORDER_COLUMNS),
            pd.DataFrame(columns=PAYMENT_COLUMNS)
        )

    # --------------------------------------------------------
    # Containers
    # --------------------------------------------------------

    sales_rows = []
    order_rows = []
    payment_rows = []

    # --------------------------------------------------------
    # Process Orders
    # --------------------------------------------------------

    for order in orders:

        order_id = order.get("orderID")
        invoice_no = order.get("invoiceNumber")
        store_id = order.get("storeID")
        order_time = order.get("orderTime")

        # ====================================================
        # 1. ITEM LEVEL → sales_fact
        # ====================================================

        for item in order.get("itemDetails", []):

            sales_rows.append(
                {
                    "order_sub_id": item.get("orderSubID"),
                    "order_id": order_id,
                    "invoice_no": invoice_no,
                    "store_id": store_id,
                    "product_id": item.get("productID"),
                    "quantity": item.get("quantity"),
                    "selling_price": item.get("rate"),
                    "mrp": item.get("MRP"),
                    "discount_amount": item.get(
                        "totalDiscountValue",
                        0
                    ),
                    "tax_amount": item.get(
                        "totalTaxValue",
                        0
                    ),
                    "sales_amount": item.get(
                        "itemSales",
                        0
                    ),
                    "order_time": order_time
                }
            )

        # ====================================================
        # 2. PAYMENT DETAILS
        # ====================================================

        payment_details = order.get(
            "paymentDetails",
            []
        )

        # Actual collected sales value
        #
        # Example:
        # transactionValue = 255.11
        # rounding         = -0.11
        # payment amount   = 255
        #
        # Therefore:
        # sales_value = 255

        sales_value = sum(
            float(
                payment.get("amount", 0) or 0
            )
            for payment in payment_details
        )

        # ====================================================
        # 3. ORDER LEVEL → sales_order
        # ====================================================

        order_rows.append(
            {
                "order_id": order_id,
                "invoice_no": invoice_no,
                "store_id": store_id,
                "order_time": order_time,

                "gross_bill": order.get(
                    "grossBill",
                    0
                ),

                "total_item_sales": order.get(
                    "totalItemSales",
                    0
                ),

                "total_discount_amount": order.get(
                    "totalDiscountValue",
                    0
                ),

                "total_tax_amount": order.get(
                    "totalTaxValue",
                    0
                ),

                "rounding": order.get(
                    "rounding",
                    0
                ),

                "transaction_value": order.get(
                    "transactionValue",
                    0
                ),

                "sales_value": sales_value,

                "total_item_count": order.get(
                    "totalItemCount",
                    0
                ),

                "total_item_quantity": order.get(
                    "totalItemQuantity",
                    0
                ),

                "payment_status": order.get(
                    "paymentStatus"
                ),

                "transaction_type": order.get(
                    "transactionType"
                )
            }
        )

        # ====================================================
        # 4. PAYMENT LEVEL → sales_payment
        # ====================================================

        for payment in payment_details:

            payment_rows.append(
                {
                    "order_id": order_id,

                    "payment_type": payment.get(
                        "type"
                    ),

                    "payment_sub_type": payment.get(
                        "subType"
                    ),

                    "payment_amount": payment.get(
                        "amount",
                        0
                    ),

                    "transaction_id": payment.get(
                        "transactionID"
                    ),

                    "last_four_digit": payment.get(
                        "lastFourDigit"
                    ),

                    "reference_id": payment.get(
                        "referenceID"
                    )
                }
            )

    # ========================================================
    # Convert to DataFrames
    # ========================================================

    sales_df = pd.DataFrame(
        sales_rows,
        columns=FINAL_COLUMNS
    )

    order_df = pd.DataFrame(
        order_rows,
        columns=ORDER_COLUMNS
    )

    payment_df = pd.DataFrame(
        payment_rows,
        columns=PAYMENT_COLUMNS
    )


    return (
        sales_df,
        order_df,
        payment_df
    )