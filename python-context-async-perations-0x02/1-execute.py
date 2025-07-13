import sqlite3

class ExecuteQuery:
    """
    A reusable class-based context manager for executing database queries.
    
    This context manager handles both database connection management and query execution,
    providing a clean interface for database operations with automatic resource cleanup.
    """
    
    def __init__(self, database_name, query, parameters=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            database_name (str): The name of the database file to connect to
            query (str): The SQL query to execute
            parameters (tuple, optional): Parameters for the SQL query
        """
        self.database_name = database_name
        self.query = query
        self.parameters = parameters or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager by opening a database connection and executing the query.
        
        This method is called when entering the 'with' statement.
        It opens the database connection, executes the query, and returns the results.
        
        Returns:
            list: The query results from fetchall()
        """
        try:
            # Open the database connection
            self.connection = sqlite3.connect(self.database_name)
            self.cursor = self.connection.cursor()
            
            print(f"Connected to database: {self.database_name}")
            print(f"Executing query: {self.query}")
            print(f"Parameters: {self.parameters}")
            
            # Execute the query with parameters
            self.cursor.execute(self.query, self.parameters)
            
            # Fetch all results
            self.results = self.cursor.fetchall()
            
            print(f"Query executed successfully. Rows returned: {len(self.results)}")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # Close connection if it was opened
            if self.connection:
                self.connection.close()
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            # Close connection if it was opened
            if self.connection:
                self.connection.close()
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager by closing the database connection.
        
        This method is called when exiting the 'with' statement.
        It ensures the database connection is properly closed, regardless of
        whether an exception occurred or not.
        
        Args:
            exc_type: The exception type (if any)
            exc_value: The exception value (if any)
            traceback: The traceback object (if any)
            
        Returns:
            bool: False to propagate any exceptions that occurred
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print(f"Disconnected from database: {self.database_name}")
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")
        
        # Return False to propagate any exceptions that occurred in the with block
        return False

# Using the ExecuteQuery context manager
if __name__ == "__main__":
    # Example 1: Query with parameters
    print("=" * 60)
    print("EXAMPLE 1: Query users with age > 25")
    print("=" * 60)
    
    with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as results:
        print("\nQuery Results:")
        print("-" * 50)
        
        if results:
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print("No users found matching the criteria.")
        
        print("-" * 50)
        print(f"Total users with age > 25: {len(results)}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Query all users")
    print("=" * 60)
    
    # Example 2: Query without parameters
    with ExecuteQuery('users.db', "SELECT * FROM users") as results:
        print("\nAll Users:")
        print("-" * 50)
        
        if results:
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print("No users found in the database.")
        
        print("-" * 50)
        print(f"Total users: {len(results)}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Query with different age threshold")
    print("=" * 60)
    
    # Example 3: Different age threshold
    with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (30,)) as results:
        print("\nUsers with age > 30:")
        print("-" * 50)
        
        if results:
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print("No users found with age > 30.")
        
        print("-" * 50)
        print(f"Total users with age > 30: {len(results)}")