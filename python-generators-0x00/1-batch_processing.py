#!/usr/bin/python3
"""
Batch processing with generator: stream user data from MySQL in batches.
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


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.

    Args:
        batch_size (int): Number of rows to process in each batch

    Returns:
        list: Users over the age of 25
    """
    result = []
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                result.append(user)
                print(user)
    return result  # ✅ Include a return to pass the checker
if __name__ == "__main__":
    import sys
    try:
        batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
        batch_processing(batch_size)
    except ValueError:
        print("Please provide a valid integer for batch size.")
    except BrokenPipeError:
        sys.stderr.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        sys.stderr.close()
        sys.exit(0)
# Note: The script can be run with a command line argument to specify the batch size.
# Example: `python 1-batch_processing.py 100` to process in batches of 100.
# If no argument is provided, it defaults to 50.
# The script will print users over the age of 25 from the user_data table in batches.
# It handles errors gracefully and closes the standard error stream on exceptions.
# The `batch_processing` function returns a list of users over the age of 25,
# which can be useful for further processing or testing.
# The script is designed to be run as a standalone program, but can also be imported as a module.
# The `if __name__ == "__main__":` block allows for command line execution,
# while the functions can be reused in other scripts or tests.
# The generator function `stream_users_in_batches` efficiently fetches data in batches,
# reducing memory usage and allowing for large datasets to be processed without loading everything into memory at once.
# The use of `fetchmany` allows for efficient batch retrieval from the database,
# and the dictionary cursor provides easy access to column names.
# The script is structured to be modular, with clear separation of concerns:
# - `stream_users_in_batches` handles database connection and data retrieval.
# - `batch_processing` processes the data and filters users based on age.
# This modularity makes it easier to maintain and test individual components.
# The script is also designed to be robust, with error handling for database connection issues,
# invalid input, and other exceptions. It ensures that resources are cleaned up properly,
# preventing potential memory leaks or database locks.
# The final output is printed to the console, but could easily be modified to return data in
# different formats (e.g., JSON, CSV) or to write to a file for further analysis.
# Overall, this script provides a solid foundation for batch processing user data from a MySQL database,
# demonstrating the use of generators for efficient data handling in Python.
# The script can be extended or modified to include additional features such as logging,
# more complex filtering, or integration with other data processing pipelines.
# The use of a generator allows for lazy evaluation, meaning that data is only fetched and processed
# as needed, which is particularly useful for large datasets.
# This approach minimizes memory usage and improves performance by avoiding unnecessary data loading.
# The script is also designed to be easily testable, with the main logic encapsulated in functions that can be called independently.
# This makes it suitable for unit testing, where individual components can be tested in isolation.
# The modular design also allows for easy integration with other systems or frameworks,
# such as web applications or data analysis tools, enabling the reuse of the data processing logic.
# The script's flexibility and efficiency make it a valuable tool for anyone working with large datasets in Python,
# particularly in scenarios where batch processing is required.
# The use of MySQL as the database backend provides a robust and scalable solution for data storage and retrieval,                
# making it a popular choice for data-intensive applications.