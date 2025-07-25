import sqlite3 
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection opening and closing.
    
    This decorator:
    1. Opens a connection to 'users.db'
    2. Passes the connection as the first argument to the decorated function
    3. Ensures the connection is properly closed after execution
    
    Args:
        func: The function to be decorated (must accept conn as first parameter)
        
    Returns:
        The wrapper function that manages database connections
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()
    
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

#### Fetch user by ID with automatic connection handling 
user = get_user_by_id(user_id=1)
print(user)