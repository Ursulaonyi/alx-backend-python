#!/usr/bin/python3
"""
Database seeding script for ALX_prodev MySQL database.
Sets up user_data table and populates it with CSV data.
"""

import mysql.connector
from mysql.connector import Error
import csv
import uuid
import os


def connect_db():
    """
    Connects to the MySQL database server.
    
    Returns:
        connection: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ursonyi@29'
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection: MySQL connection object to ALX_prodev database or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Ursonyi@29',
            database='ALX_prodev'
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        
        # Create table with specified schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data from CSV file into the database if it does not exist.
    
    Args:
        connection: MySQL connection object
        csv_file: Path to the CSV file containing user data
    """
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Data already exists in table ({count} rows). Skipping insertion.")
            cursor.close()
            return
        
        # Read and insert data from CSV
        if not os.path.exists(csv_file):
            print(f"CSV file '{csv_file}' not found. Creating sample data...")
            create_sample_csv(csv_file)
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            
            data_to_insert = []
            for row in csv_reader:
                # Generate UUID for user_id if not present, or use existing
                user_id = row.get('user_id', str(uuid.uuid4()))
                name = row['name']
                email = row['email']
                age = int(float(row['age']))  # Convert to int from decimal
                
                data_to_insert.append((user_id, name, email, age))
            
            # Insert data in batches
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            
            print(f"Successfully inserted {len(data_to_insert)} rows into user_data table")
        
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Error processing CSV file: {e}")


def create_sample_csv(filename):
    """
    Creates a sample CSV file with user data for testing purposes.
    
    Args:
        filename: Name of the CSV file to create
    """
    sample_data = [
        {'user_id': '00234e50-34eb-4ce2-94ec-26e3fa749796', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67},
        {'user_id': '006bfede-724d-4cdd-a2a6-59700f40d0da', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119},
        {'user_id': '006e1f7f-90c2-45ad-8c1d-1275d594cc88', 'name': 'Daniel Fahey IV', 'email': 'Delia.Lesch11@hotmail.com', 'age': 49},
        {'user_id': '00af05c9-0a86-419e-8c2d-5fb7e899ae1c', 'name': 'Ronnie Bechtelar', 'email': 'Sandra19@yahoo.com', 'age': 22},
        {'user_id': '00cc08cc-62f4-4da1-b8e4-f5d9ef5dbbd4', 'name': 'Alma Bechtelar', 'email': 'Shelly_Balistreri22@hotmail.com', 'age': 102}
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['user_id', 'name', 'email', 'age']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"Sample CSV file '{filename}' created successfully")


if __name__ == "__main__":
    # Test the functions
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        
        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')
            connection.close()