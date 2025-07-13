#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries

This module demonstrates running multiple database queries concurrently
using asyncio.gather() and aiosqlite for asynchronous SQLite operations.
"""

import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: List of all user records from the database
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users') as cursor:
            users = await cursor.fetchall()
            print(f"Fetched {len(users)} users")
            return users


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: List of user records where age > 40
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users WHERE age > 40') as cursor:
            older_users = await cursor.fetchall()
            print(f"Fetched {len(older_users)} users older than 40")
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
    async with aiosqlite.connect('users.db') as db:
        # Create users table
        await db.execute('''
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
        await db.executemany('''
            INSERT OR REPLACE INTO users (id, name, age, email)
            VALUES (?, ?, ?, ?)
        ''', sample_users)
        
        await db.commit()
        print("Sample database created with users data")


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