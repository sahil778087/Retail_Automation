from shared.database.connection import get_connection


def main():

    conn = get_connection()

    print(conn)

    conn.close()

    print("✓ Connection Closed")


if __name__ == "__main__":

    main()