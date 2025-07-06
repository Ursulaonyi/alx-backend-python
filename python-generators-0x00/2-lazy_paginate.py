#!/usr/bin/python3
"""
Lazy pagination generator for efficiently loading paginated data from database.
Uses yield to fetch pages only when needed, starting from offset 0.
"""

import mysql.connector
from mysql.connector import Error


def paginate_users(page_size, offset):
    """
    Fetch a page of users from the database at a specific offset.
    
    Args:
        page_size (int): Number of users to fetch per page
        offset (int): Starting position for the page
        
    Returns:
        list: List of user dictionaries for the current page
    """
    connection = None
    cursor = None
    
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ursonyi@29',
            database='ALX_prodev'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
            rows = cursor.fetchall()
            return rows
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return []
    
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def lazy_paginate(page_size):
    """
    Generator that lazily loads paginated data from the users database.
    Fetches pages only when needed, starting from offset 0.
    
    Args:
        page_size (int): Number of users to fetch per page
        
    Yields:
        list: A page of user data as a list of dictionaries
    """
    offset = 0
    
    # Single loop to fetch pages lazily
    while True:
        page = paginate_users(page_size, offset)
        
        # If no more data, stop the generator
        if not page:
            break
            
        yield page
        offset += page_size


# Alias for the function name used in the test
lazy_pagination = lazy_paginate