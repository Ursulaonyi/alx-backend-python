# Python Generators Project - Advanced Data Processing

## About The Project

This project introduces advanced usage of Python generators to efficiently handle large datasets, process data in batches, and simulate real-world scenarios involving live updates and memory-efficient computations. The tasks focus on leveraging Python's `yield` keyword to implement generators that provide iterative access to data, promoting optimal resource utilization, and improving performance in data-driven applications.

## Learning Objectives

By completing this project, you will:

1. **Master Python Generators**: Learn to create and utilize generators for iterative data processing, enabling memory-efficient operations.
2. **Handle Large Datasets**: Implement batch processing and lazy loading to work with extensive datasets without overloading memory.
3. **Simulate Real-world Scenarios**: Develop solutions to simulate live data updates and apply them to streaming contexts.
4. **Optimize Performance**: Use generators to calculate aggregate functions like averages on large datasets, minimizing memory consumption.
5. **Apply SQL Knowledge**: Use SQL queries to fetch data dynamically, integrating Python with databases for robust data management.

## Requirements

- Python 3.x proficiency
- Understanding of `yield` and Python's generator functions
- Familiarity with SQL and database operations (MySQL and SQLite)
- Basic knowledge of database schema design and data seeding
- Git and GitHub for version control and submission

## Project Structure

```
python-generators-0x00/
├── README.md
├── 0-main.py          # Test script for database setup
├── seed.py            # Database seeding and setup script
├── user_data.csv      # Sample data file (auto-generated)
└── requirements.txt   # Python dependencies
```

## Getting Started

### Prerequisites

1. **Python 3.x** installed on your system
2. **MySQL Server** running locally
3. **MySQL credentials** (username and password)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-generators-0x00
   ```

2. **Install required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install mysql-connector-python
   ```

3. **Set up MySQL Database**:
   - Ensure MySQL server is running
   - Update database credentials in `seed.py` if needed (current setup uses root/Ursonyi@29)

### Usage

#### Task 0: Getting Started with Python Generators

**Objective**: Create a generator that streams rows from an SQL database one by one.

1. **Run the database setup**:
   ```bash
   python3 ./0-main.py
   ```

2. **Expected Output**:
   ```
   Successfully connected to MySQL server
   Database ALX_prodev created successfully or already exists
   connection successful
   Successfully connected to ALX_prodev database
   Table user_data created successfully
   Sample CSV file 'user_data.csv' created successfully
   Successfully inserted 5 rows into user_data table
   Database ALX_prodev is present 
   [('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), 
    ('006bfede-724d-4cdd-a2a6-59700f40d0da', 'Glenda Wisozk', 'Miriam21@gmail.com', 119), 
    ('006e1f7f-90c2-45ad-8c1d-1275d594cc88', 'Daniel Fahey IV', 'Delia.Lesch11@hotmail.com', 49), 
    ('00af05c9-0a86-419e-8c2d-5fb7e899ae1c', 'Ronnie Bechtelar', 'Sandra19@yahoo.com', 22), 
    ('00cc08cc-62f4-4da1-b8e4-f5d9ef5dbbd4', 'Alma Bechtelar', 'Shelly_Balistreri22@hotmail.com', 102)]
   ```

## Database Schema

The project creates a MySQL database called `ALX_prodev` with the following table:

### user_data Table
| Column   | Type         | Constraints                    |
|----------|--------------|--------------------------------|
| user_id  | VARCHAR(36)  | PRIMARY KEY, Indexed           |
| name     | VARCHAR(255) | NOT NULL                       |
| email    | VARCHAR(255) | NOT NULL                       |
| age      | DECIMAL(3,0) | NOT NULL                       |

## Key Functions

### seed.py Functions

- **`connect_db()`**: Connects to the MySQL database server
- **`create_database(connection)`**: Creates the database `ALX_prodev` if it does not exist
- **`connect_to_prodev()`**: Connects to the ALX_prodev database in MySQL
- **`create_table(connection)`**: Creates the user_data table if it doesn't exist
- **`insert_data(connection, data)`**: Inserts data from CSV file into the database

## Features

- **Automatic Database Setup**: Creates database and table structure automatically
- **Sample Data Generation**: Generates sample CSV data if file doesn't exist
- **Error Handling**: Comprehensive error handling for database operations
- **Duplicate Prevention**: Checks for existing data before insertion
- **Memory Efficient**: Uses generators for streaming data processing

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**:
   - Ensure MySQL server is running
   - Verify credentials in `seed.py`
   - Check if MySQL service is accessible on localhost

2. **Permission Errors**:
   - Make sure scripts are executable: `chmod +x 0-main.py seed.py`
   - Check MySQL user permissions

3. **Module Import Errors**:
   - Install required packages: `pip install mysql-connector-python`
   - Ensure Python 3.x is being used

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is part of the ALX Backend Python curriculum.

## Contact

For questions or issues, please contact the project maintainers.

---

**Note**: This is Task 0 of the Python Generators project. Additional tasks will be added as the project progresses, focusing on advanced generator usage, batch processing, and real-world data streaming scenarios.