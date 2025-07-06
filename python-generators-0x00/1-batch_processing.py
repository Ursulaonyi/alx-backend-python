#!/usr/bin/python3
"""
Generator that fetches user_data in batches from a MySQL database.
"""

import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from the user_data table in batches.

    Args:
        batch_size (int): Number of rows to fetch in each batch

    Yields:
        list: A list of dictionaries representing a batch of user data
    """
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ursonyi@29',
            database='ALX_prodev'
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, age FROM user_data")

            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                yield batch

    except Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
# Example usage:
# if __name__ == "__main__":
#     for batch in stream_users_in_batches(5):  # Fetch 5 rows at a time
#         print(batch)  # Process the batch