from shared.database.connection import get_connection
from shared.database.repositories.run_repository import (
    create_run,
    complete_run
)


def main():

    conn = get_connection()

    try:

        run_uuid = create_run(conn)

        print(f"Run UUID : {run_uuid}")

        complete_run(
            connection=conn,
            run_uuid=run_uuid,
            stores_processed=5,
            stores_failed=0,
            products_processed=250,
            rows_inserted=250,
            duration_seconds=10.45
        )

        conn.commit()

        print("Run Saved Successfully")

    except Exception as e:

        conn.rollback()

        print(e)

    finally:

        conn.close()


if __name__ == "__main__":
    main()