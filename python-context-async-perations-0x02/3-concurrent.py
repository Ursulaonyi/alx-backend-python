#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries

This module demonstrates running multiple database queries concurrently
using asyncio.gather() and custom DatabaseConnection context manager.
"""

import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor


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


def sync_fetch_users():
    """
    Synchronously fetch all users from the database using DatabaseConnection context manager.
    
    Returns:
        list: List of all user records from the database
    """
    with DatabaseConnection('users.db') as cursor:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        print(f"Fetched {len(users)} users")
        return users


def sync_fetch_older_users():
    """
    Synchronously fetch users older than 40 from the database using DatabaseConnection context manager.
    
    Returns:
        list: List of user records where age > 40
    """
    with DatabaseConnection('users.db') as cursor:
        cursor.execute('SELECT * FROM users WHERE age > 40')
        older_users = cursor.fetchall()
        print(f"Fetched {len(older_users)} users older than 40")
        return older_users


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database by running sync function in thread pool.
    
    Returns:
        list: List of all user records from the database
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        users = await loop.run_in_executor(executor, sync_fetch_users)
        return users


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database by running sync function in thread pool.
    
    Returns:
        list: List of user records where age > 40
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        older_users = await loop.run_in_executor(executor, sync_fetch_older_users)
        return older_users


async def fetch_concurrently():
    """
    Execute multiple database queries concurrently using asyncio.gather().
    
    This function runs both async_fetch_users() and async_fetch_older_users()
    concurrently, which is more efficient than running them sequentially.
    
    Returns:
        tuple: A tuple containing (all_users, older_users)
    """
    print("Starting concurrent database queries...")
    
    # Use asyncio.gather to run both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("Concurrent queries completed!")
    return all_users, older_users


async def create_sample_database():
    """
    Create a sample database with users table for testing purposes.
    This function is for demonstration and testing.
    """
    def create_db():
        with DatabaseConnection('users.db') as cursor:
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')
            
            # Insert sample data
            sample_users = [
                (1, 'Alice Johnson', 28, 'alice@example.com'),
                (2, 'Bob Smith', 45, 'bob@example.com'),
                (3, 'Charlie Brown', 35, 'charlie@example.com'),
                (4, 'Diana Prince', 42, 'diana@example.com'),
                (5, 'Eve Wilson', 38, 'eve@example.com'),
                (6, 'Frank Miller', 51, 'frank@example.com'),
                (7, 'Grace Lee', 29, 'grace@example.com'),
                (8, 'Henry Davis', 47, 'henry@example.com'),
            ]
            
            # Use INSERT OR REPLACE to avoid conflicts if running multiple times
            cursor.executemany('''
                INSERT OR REPLACE INTO users (id, name, age, email)
                VALUES (?, ?, ?, ?)
            ''', sample_users)
            
            cursor.connection.commit()
            print("Sample database created with users data")
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, create_db)


async def main():
    """
    Main function to demonstrate concurrent database operations.
    """
    # Create sample database for testing
    await create_sample_database()
    
    # Run concurrent queries
    all_users, older_users = await fetch_concurrently()
    
    # Display results
    print(f"\nAll Users ({len(all_users)}):")
    for user in all_users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
    
    print(f"\nUsers older than 40 ({len(older_users)}):")
    for user in older_users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")


if __name__ == "__main__":
    # Use asyncio.run to run the concurrent fetch as specified
    asyncio.run(main())