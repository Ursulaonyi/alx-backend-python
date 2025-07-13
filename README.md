# alx-backend-python

# 🌀 Python Generators – Advanced Data Handling

## 📚 Project Overview

This project explores advanced use of **Python generators** to handle large datasets efficiently. Through memory-optimized, lazy-loading techniques and real-world database operations, it demonstrates how Python's `yield` keyword can streamline data processing in modern applications.

> **Start Date:** Jun 30, 2025  
> **End Date:** Jul 7, 2025  
> **Project Level:** Novice  
> **Weight:** 1  
> **Manual QA Required:** ✅  

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

> **Start Date:** Jul 8, 2025  
> **End Date:** Jul 15, 2025  
> **Project Level:** Intermediate  
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

## 🛠️ Requirements

1. Python 3.8 or higher installed.
2. SQLite3 database setup with a `users` table for testing.
3. A working knowledge of Python decorators and database operations.
4. Familiarity with Git and GitHub for project submission.
5. Strong problem-solving skills and attention to detail.

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

## 🔧 Key Decorator Patterns

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

### Execution Order
Decorators are applied from bottom to top:
1. `@cache_query` (innermost - executes first)
2. `@retry_on_failure` 
3. `@transactional`
4. `@with_db_connection` (outermost - executes last)

---

## 📈 Performance Benefits

- **Memory Efficiency**: Generators reduce memory usage for large datasets
- **Query Optimization**: Caching eliminates redundant database calls
- **Resilience**: Retry mechanisms handle transient failures
- **Clean Code**: Decorators separate concerns and reduce boilerplate
- **Maintainability**: Reusable patterns across different functions

---

## ✅ Final Notes

- Ensure your MySQL server is running for generators project
- Ensure your SQLite database (`users.db`) exists for decorators project
- Replace your credentials (username/password) in each script as needed
- Always close your DB connections in a `finally` block
- Test decorator combinations thoroughly
- Consider cache invalidation strategies for production use

---

## 🎓 Skills Developed

- **Advanced Python Patterns**: Generators, decorators, context managers
- **Database Optimization**: Connection pooling, query caching, transaction management
- **Error Handling**: Retry mechanisms, graceful degradation
- **Performance Tuning**: Memory efficiency, query optimization
- **Clean Architecture**: Separation of concerns, reusable components
- **Production Readiness**: Logging, monitoring, resilience patterns