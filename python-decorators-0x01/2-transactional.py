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

def transactional(func):
    """
    Decorator that manages database transactions with automatic commit/rollback.
    
    This decorator:
    1. Begins a transaction (implicit in SQLite)
    2. Executes the decorated function
    3. Commits the transaction if successful
    4. Rolls back the transaction if an exception occurs
    5. Re-raises any exceptions that occurred
    
    Args:
        func: The function to be decorated (must accept conn as first parameter)
        
    Returns:
        The wrapper function that manages transactions
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function within a transaction
            result = func(conn, *args, **kwargs)
            
            # If function succeeds, commit the transaction
            conn.commit()
            return result
            
        except Exception as e:
            # If an exception occurs, rollback the transaction
            conn.rollback()
            # Re-raise the exception to maintain error propagation
            raise e
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')