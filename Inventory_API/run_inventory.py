import pandas as pd

from shared.auth import get_partner_token
from shared.store_loader import load_stores
from shared.inventory_parser import parse_inventory
from shared.exporter import export_inventory

from Inventory_API.qb_inventory_api import fetch_store_inventory


def main():

    print("=" * 60)
    print("QUEUEBUSTER INVENTORY REFRESH")
    print("=" * 60)

    # ----------------------------------------
    # Generate Partner Token
    # ----------------------------------------

    auth = get_partner_token()
    token = auth["token"]

    print("\n✓ Partner Token Generated")
    print(f"Issued At : {auth['issued_at']}")
    print(f"Expires   : {auth['expires']}")

    # ----------------------------------------
    # Load Stores
    # ----------------------------------------

    stores = load_stores()

    print(f"\n✓ Loaded {len(stores)} Stores\n")

    inventory_frames = []

    # ----------------------------------------
    # Process Every Store
    # ----------------------------------------

    for _, store in stores.iterrows():

        store_id = int(store["storeID"])
        store_name = str(store["storeName"])

        print(f"\nFetching : {store_name}")

        try:

            response = fetch_store_inventory(
                store_id=store_id,
                token=token
            )

            df = parse_inventory(
                response=response,
                store_id=store_id,
                store_name=store_name
            )

            inventory_frames.append(df)

            print(f"✓ Products : {len(df)}")

        except Exception as e:

            print(f"✗ Failed : {store_name}")
            print(e)

    # ----------------------------------------
    # Safety Check
    # ----------------------------------------

    if not inventory_frames:
        raise Exception("No inventory data was fetched.")

    # ----------------------------------------
    # Merge Everything
    # ----------------------------------------

    final_df = pd.concat(
        inventory_frames,
        ignore_index=True
    )

    # ----------------------------------------
    # Export CSV
    # ----------------------------------------

    export_inventory(final_df)

    print("\n========================================")
    print("Inventory Refresh Completed Successfully")
    print("========================================")

    print(f"Stores Processed : {len(inventory_frames)}")
    print(f"Rows Exported    : {len(final_df):,}")


if __name__ == "__main__":
    main()