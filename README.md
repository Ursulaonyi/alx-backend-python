# alx-backend-python

# 🌀 Python Generators – Advanced Data Handling

## 📚 Project Overview

This project explores advanced use of **Python generators** to handle large datasets efficiently. Through memory-optimized, lazy-loading techniques and real-world database operations, it demonstrates how Python's `yield` keyword can streamline data processing in modern applications.

---

## 🎯 Learning Objectives

By completing this project, you will:

- ✅ Master Python generator functions using `yield`
- ✅ Stream large datasets without consuming excessive memory
- ✅ Implement batch processing and lazy pagination
- ✅ Simulate live streaming data operations
- ✅ Optimize performance using generator-based aggregate functions
- ✅ Integrate SQL querying with Python logic

---

## 🛠️ Requirements

- Python 3.x
- MySQL Server
- `mysql-connector-python` library
- Basic understanding of:
  - Python's `yield` and generator expressions
  - SQL operations and queries (SELECT, INSERT, LIMIT, OFFSET)
  - Database schema and indexing
  - Git and GitHub for version control

Install the MySQL connector:

```bash
pip install mysql-connector-python
```

---

# 🔄 Python Context Managers & Async Operations

## 📚 Project Overview

This project focuses on mastering **Python context managers** and **asynchronous operations** to handle database connections efficiently and perform concurrent operations. Through practical implementations, learners will create custom context managers for database operations and implement asynchronous patterns for improved performance.

> **Start Date:** Jul 8, 2025  
> **End Date:** Jul 15, 2025  
> **Project Level:** Intermediate  
> **Weight:** 1  
> **Manual QA Required:** ✅  

---

## 🎯 Learning Objectives

By completing this project, you will:

- ✅ Master Python context managers using `__enter__` and `__exit__` methods
- ✅ Implement custom database connection context managers
- ✅ Create reusable query execution context managers
- ✅ Understand asynchronous programming with `asyncio` and `aiosqlite`
- ✅ Implement concurrent database operations using `asyncio.gather()`
- ✅ Optimize database performance through asynchronous operations
- ✅ Handle resource management and cleanup automatically

---

## 🛠️ Requirements

- Python 3.8 or higher
- SQLite3 database support
- `aiosqlite` library for async database operations
- Understanding of:
  - Python context managers and `with` statements
  - Asynchronous programming concepts
  - Database operations and SQL
  - Git and GitHub for version control

Install required packages:

```bash
pip install aiosqlite
```

---

## 🗂️ Directory Structure

```
alx-backend-python/
├── python-generators-0x00/
│   ├── seed.py
│   ├── 0-stream_users.py
│   ├── 1-batch_processing.py
│   ├── 2-lazy_paginate.py
│   ├── 3-main.py
│   ├── 4-stream_ages.py
│   ├── user_data.csv
│   └── README.md
├── python-context-async-perations-0x02/
│   ├── 0-databaseconnection.py
│   ├── 1-execute.py
│   ├── 3-concurrent.py
│   └── README.md
└── python-decorators-0x01/
    ├── 0-log_queries.py
    ├── 1-with_db_connection.py
    ├── 2-transactional.py
    ├── 3-retry_on_failure.py
    ├── 4-cache_query.py
    └── README.md
```

---

# 🎨 Python Decorators – Advanced Database Operations

## 📚 Project Overview

This project focuses on mastering **Python decorators** to enhance database operations in Python applications. Through hands-on tasks, learners create custom decorators to log queries, handle connections, manage transactions, retry failed operations, and cache query results. The tasks simulate real-world challenges, providing an in-depth understanding of Python's capabilities for dynamic and reusable code in database management.

> **Start Date:** Jul 16, 2025  
> **End Date:** Jul 23, 2025  
> **Project Level:** Advanced  
> **Weight:** 1  
> **Manual QA Required:** ✅  

---

## 🎯 Learning Objectives

By completing this project, professional developers will:

1. **Deepen their knowledge of Python decorators** and how they can be used to create reusable, efficient, and clean code.
2. **Enhance database management skills** by automating repetitive tasks like connection handling, logging, and caching.
3. **Implement robust transaction management techniques** to ensure data integrity and handle errors gracefully.
4. **Optimize database queries** by leveraging caching mechanisms to reduce redundant calls.
5. **Build resilience into database operations** by implementing retry mechanisms for transient errors.
6. **Apply best practices in database interaction** for scalable and maintainable Python applications.

---

## 📌 Tasks Breakdown

### **Generators Project (python-generators-0x00/)**

#### 0. Getting Started with Python Generators  
**File:** `seed.py`  
- Connect to MySQL and create `ALX_prodev` database  
- Create `user_data` table with fields: `user_id`, `name`, `email`, `age`  
- Load data from `user_data.csv`

#### 1. Stream Users One by One  
**File:** `0-stream_users.py`  
- Function: `def stream_users()`  
- Use a generator to yield user records one at a time  
- Only 1 loop allowed

#### 2. Batch Processing Large Data  
**File:** `1-batch_processing.py`  
- Functions:  
  - `stream_users_in_batches(batch_size)`  
  - `batch_processing(batch_size)`  
- Fetch and filter users over age 25  
- Use `yield` and no more than 3 loops

#### 3. Lazy Loading with Pagination  
**File:** `2-lazy_paginate.py`  
- Function: `lazy_pagination(page_size)`  
- Includes `paginate_users(page_size, offset)` helper  
- Uses `yield` and just 1 loop

#### 4. Memory-Efficient Aggregation  
**File:** `4-stream_ages.py`  
- Function: `stream_user_ages()` yields each age  
- Function: `compute_average_age()` calculates average  
- No SQL `AVG()` allowed  
- No more than 2 loops

---

### **Context Managers & Async Operations Project (python-context-async-perations-0x02/)**

#### 0. Custom Database Connection Context Manager  
**File:** `0-databaseconnection.py`  
- **Objective:** Create a custom class-based context manager for database connections
- **Features:**
  - Implements `__enter__` and `__exit__` methods
  - Automatically handles SQLite database connection and cleanup
  - Provides cursor for query execution
  - Ensures proper resource management and error handling
- **Class:** `DatabaseConnection`

#### 1. Query Execution Context Manager  
**File:** `1-execute.py`  
- **Objective:** Create a reusable context manager for executing database queries
- **Features:**
  - Handles both database connection and query execution
  - Supports parameterized queries for security
  - Automatically fetches and returns query results
  - Combines connection management with query execution
- **Class:** `ExecuteQuery`

#### 2. Concurrent Asynchronous Database Queries  
**File:** `3-concurrent.py`  
- **Objective:** Implement concurrent database operations using asyncio
- **Features:**
  - Uses `aiosqlite` for asynchronous SQLite operations
  - Implements two async functions: `async_fetch_users()` and `async_fetch_older_users()`
  - Uses `asyncio.gather()` to execute queries concurrently
  - Demonstrates performance benefits of async operations
- **Functions:** 
  - `async_fetch_users()` - fetches all users
  - `async_fetch_older_users()` - fetches users older than 40
  - `fetch_concurrently()` - runs both queries concurrently

---

### **Decorators Project (python-decorators-0x01/)**

#### 0. Logging Database Queries  
**File:** `0-log_queries.py`  
- **Objective:** Create a decorator that logs database queries executed by any function
- **Features:**
  - Logs SQL queries with timestamps using `datetime`
  - Intercepts function calls to enhance observability
  - Format: `[YYYY-MM-DD HH:MM:SS] Executing query: SQL_QUERY`
- **Prototype:** `def log_queries(func)`

#### 1. Handle Database Connections with a Decorator  
**File:** `1-with_db_connection.py`  
- **Objective:** Create a decorator that automatically handles opening and closing database connections
- **Features:**
  - Opens SQLite connection to `users.db`
  - Passes connection as first parameter to decorated function
  - Ensures connection is properly closed using `try/finally`
  - Eliminates boilerplate connection management code
- **Prototype:** `def with_db_connection(func)`

#### 2. Transaction Management Decorator  
**File:** `2-transactional.py`  
- **Objective:** Create a decorator that manages database transactions by automatically committing or rolling back changes
- **Features:**
  - Wraps function execution in database transaction
  - Commits transaction on successful execution
  - Rolls back transaction on any exception
  - Ensures data integrity and consistency
  - Works with `@with_db_connection` decorator
- **Prototype:** `def transactional(func)`

#### 3. Retry Database Queries  
**File:** `3-retry_on_failure.py`  
- **Objective:** Create a decorator that retries database operations if they fail due to transient errors
- **Features:**
  - Configurable retry count and delay between attempts
  - Logs retry attempts and failures
  - Introduces resilience against transient database issues
  - Raises final exception if all retries fail
- **Prototype:** `def retry_on_failure(retries=3, delay=2)`

#### 4. Cache Database Queries  
**File:** `4-cache_query.py`  
- **Objective:** Create a decorator that caches the results of database queries to avoid redundant calls
- **Features:**
  - Uses SQL query string as cache key
  - Stores results in global `query_cache` dictionary
  - Provides cache hit/miss feedback
  - Optimizes performance by avoiding redundant database calls
- **Prototype:** `def cache_query(func)`

---

## ✅ Example Output

### Context Managers & Async Operations:
```bash
# Database Connection Context Manager
Connected to database: users.db
Query Results:
--------------------------------------------------
ID: 1, Name: John Doe, Email: john@example.com, Age: 30
ID: 2, Name: Jane Smith, Email: jane@example.com, Age: 25
--------------------------------------------------
Total users: 2
Disconnected from database: users.db

# Concurrent Async Operations
Starting concurrent database queries...
Connected to database: users.db
Fetched 8 users
Connected to database: users.db
Fetched 4 users older than 40
Concurrent queries completed!
```

### Generators Project:
```bash
Average age of users: 47.25
```

### Decorators Project:
```bash
# Logging Decorator
[2025-07-13 10:30:45] Executing query: SELECT * FROM users

# Cache Decorator
Cache miss for query: SELECT * FROM users
Cache hit for query: SELECT * FROM users

# Retry Decorator
Attempt 1 failed: database is locked. Retrying in 1 seconds...
Attempt 2 failed: database is locked. Retrying in 1 seconds...
```

---

## 🧪 Testing Scripts

Each main test file is named like `N-main.py`, for example:

```bash
python3 2-main.py
./3-main.py
```

Use `head`, `tail`, or `islice()` in your test scripts to limit the output when streaming large results.

---

## 🔧 Key Patterns & Benefits

### Context Manager Benefits
- **Automatic Resource Management**: Ensures database connections are properly closed
- **Error Handling**: Cleanup occurs even when exceptions happen
- **Code Reusability**: Same context manager can be used across multiple functions
- **Clean Code**: Eliminates boilerplate connection management

### Asynchronous Programming Benefits
- **Concurrent Operations**: Multiple database queries can run simultaneously
- **Improved Performance**: I/O operations don't block the main thread
- **Better Resource Utilization**: CPU can handle other tasks while waiting for database responses
- **Scalability**: Applications can handle more concurrent users

### Decorator Stacking
Multiple decorators can be combined for powerful functionality:

```python
@with_db_connection
@transactional
@retry_on_failure(retries=3, delay=1)
@cache_query
def complex_database_operation(conn, query):
    # Your database logic here
    pass
```

### Context Manager with Async
```python
async with aiosqlite.connect('users.db') as db:
    async with db.execute('SELECT * FROM users') as cursor:
        results = await cursor.fetchall()
```

---

## 📈 Performance Benefits

- **Memory Efficiency**: Generators reduce memory usage for large datasets
- **Concurrent Processing**: Async operations improve throughput
- **Query Optimization**: Caching eliminates redundant database calls
- **Resilience**: Retry mechanisms handle transient failures
- **Clean Code**: Context managers and decorators separate concerns
- **Maintainability**: Reusable patterns across different functions

---

## ✅ Final Notes

- Ensure your MySQL server is running for generators project
- Ensure your SQLite database (`users.db`) exists for context managers and decorators projects
- Install `aiosqlite` for async database operations: `pip install aiosqlite`
- Replace your credentials (username/password) in each script as needed
- Always use proper resource management with context managers
- Test async operations thoroughly to ensure proper concurrent execution
- Consider cache invalidation strategies for production use

---

## 🎓 Skills Developed

- **Advanced Python Patterns**: Generators, context managers, decorators, async programming
- **Database Optimization**: Connection management, query caching, concurrent operations
- **Error Handling**: Resource cleanup, retry mechanisms, graceful degradation
- **Performance Tuning**: Memory efficiency, async operations, query optimization
- **Clean Architecture**: Separation of concerns, reusable components
- **Production Readiness**: Logging, monitoring, resilience patterns
- **Concurrent Programming**: Async/await, `asyncio.gather()`, thread safety