import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before executing the decorated function.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapper function that logs queries and calls the original function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        # Assuming the query is passed as a keyword argument or first positional argument
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is the first positional argument
        elif args:
            query = args[0]
        
        # Log the query if found
        if query:
            print(f"Executing query: {query}")
        
        # Call the original function with all arguments
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")