import mysql.connector

from mysql.connector import Error

from shared.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)


def get_connection():
    """
    Creates and returns a MySQL database connection.
    """

    try:

        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=False
        )

        if connection.is_connected():

            print("✓ Connected to MySQL")

            return connection

        raise ConnectionError("Unable to establish database connection.")

    except Error as e:

        raise RuntimeError(f"MySQL Connection Error : {e}")