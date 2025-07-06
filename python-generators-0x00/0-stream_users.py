#!/usr/bin/python3
"""
Generator function to stream rows from SQL database one by one.
Uses yield to create a memory-efficient iterator for database rows.
"""

import mysql.connector
from mysql.connector import Error


def stream_users():
    """
    Generator that streams rows from the user_data table one by one.
    
    Yields:
        dict: A dictionary containing user data with keys: user_id, name, email, age
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
            
            # Execute query to fetch all users
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            # Use generator to yield rows one by one
            for row in cursor:
                yield row
                
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()