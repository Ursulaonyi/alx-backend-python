import time
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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries database operations if they fail due to transient errors.
    
    This decorator:
    1. Attempts to execute the decorated function
    2. If it fails, waits for the specified delay
    3. Retries up to the specified number of times
    4. Raises the last exception if all retries are exhausted
    
    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (int): Delay in seconds between retries (default: 2)
        
    Returns:
        The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # Try the function execution up to (retries + 1) times
            for attempt in range(retries + 1):
                try:
                    # Attempt to execute the function
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # If this is the last attempt, don't wait
                    if attempt == retries:
                        break
                    
                    # Wait before the next retry
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            
            # If all retries are exhausted, raise the last exception
            print(f"All {retries + 1} attempts failed. Raising last exception.")
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)