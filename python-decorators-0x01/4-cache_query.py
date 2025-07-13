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

query_cache = {}

def cache_query(func):
    """
    Decorator that caches the results of database queries to avoid redundant calls.
    
    This decorator:
    1. Checks if the query result is already cached
    2. If cached, returns the cached result immediately
    3. If not cached, executes the function and caches the result
    4. Uses the SQL query string as the cache key
    
    Args:
        func: The function to be decorated (must accept query as a parameter)
        
    Returns:
        The wrapper function that manages query caching
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is in args (assuming it's the second argument after conn)
        elif len(args) > 1:
            query = args[1]
        
        # If we can't find the query, execute without caching
        if query is None:
            return func(*args, **kwargs)
        
        # Check if the query result is already cached
        if query in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[query]
        
        # Query not in cache, execute the function
        print(f"Cache miss for query: {query}")
        result = func(*args, **kwargs)
        
        # Cache the result using the query as the key
        query_cache[query] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")