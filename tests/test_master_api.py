from shared.auth import get_partner_token

from Master_API.qb_category_api import fetch_categories
from Master_API.qb_subcategory_api import fetch_sub_categories
from Master_API.qb_brand_api import fetch_brands
from Master_API.qb_product_api import fetch_products
from shared.category_parser import parse_categories
from shared.sub_category_parser import parse_sub_categories
from shared.brand_parser import parse_brands
from shared.product_parser import (
    parse_products,
    parse_product_barcodes
)


def main():

    auth = get_partner_token()

    token = auth["token"]

    print("\nCATEGORY")
    category_response = fetch_categories(token)
    category_df = parse_categories(
        category_response
    )

    print("\nParsed Categories:")
    print(category_df)

    print("\nColumns:")
    print(category_df.columns.tolist())

    print("\nRows:")
    print(len(category_df))
    print(category_response["status"])
    print(category_response["message"])
    print("Records:", len(category_response.get("data", [])))


    print("\nSUB CATEGORY")
    sub_category_response = fetch_sub_categories(token)

    sub_category_df = parse_sub_categories(
        sub_category_response
    )

    print("\nParsed Sub Categories:")
    print(sub_category_df)

    print("\nColumns:")
    print(sub_category_df.columns.tolist())

    print("\nRows:")
    print(len(sub_category_df))

    print(sub_category_response["status"])
    print(sub_category_response["message"])
    print("Records:", len(sub_category_response.get("data", [])))


    print("\nBRAND")
    brand_response = fetch_brands(token)

    brand_df = parse_brands(
        brand_response
    )

    print("\nParsed Brands:")
    print(brand_df)

    print("\nColumns:")
    print(brand_df.columns.tolist())

    print("\nRows:")
    print(len(brand_df))

    print(brand_response["status"])
    print(brand_response["message"])
    print("Records:", len(brand_response.get("data", [])))


    print("\nPRODUCT")
    product_response = fetch_products(token)
           
    product_df = parse_products(
        product_response
    )

    barcode_df = parse_product_barcodes(
        product_response
    )

    print("\nParsed Products:")
    print(product_df.head())

    print("\nProduct Columns:")
    print(product_df.columns.tolist())

    print("\nProduct Rows:")
    print(len(product_df))

    print("\nParsed Barcodes:")
    print(barcode_df.head(20))

    print("\nBarcode Columns:")
    print(barcode_df.columns.tolist())

    print("\nBarcode Rows:")
    print(len(barcode_df))

    print(product_response["status"])
    print(product_response["message"])
    print("Records:", len(product_response.get("data", [])))


if __name__ == "__main__":
    main()