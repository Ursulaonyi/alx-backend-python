import sqlite3

class DatabaseConnection:
    """
    A custom class-based context manager for handling database connections.
    
    This context manager automatically handles opening and closing database connections
    using the __enter__ and __exit__ methods, ensuring proper resource management.
    """
    
    def __init__(self, database_name):
        """
        Initialize the DatabaseConnection context manager.
        
        Args:
            database_name (str): The name of the database file to connect to
        """
        self.database_name = database_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager by opening a database connection.
        
        This method is called when entering the 'with' statement.
        It opens the database connection and returns the cursor for query execution.
        
        Returns:
            sqlite3.Cursor: The database cursor for executing queries
        """
        try:
            # Open the database connection
            self.connection = sqlite3.connect(self.database_name)
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {self.database_name}")
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
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

# Using the context manager with the 'with' statement
if __name__ == "__main__":
    # Create and use the DatabaseConnection context manager
    with DatabaseConnection('users.db') as cursor:
        # Execute the query
        cursor.execute("SELECT * FROM users")
        
        # Fetch and print all results
        results = cursor.fetchall()
        
        print("\nQuery Results:")
        print("-" * 50)
        
        if results:
            for row in results:
                print(row)
        else:
            print("No users found in the database.")
        
        print("-" * 50)
        print(f"Total users: {len(results)}")