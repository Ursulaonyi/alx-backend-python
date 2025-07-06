# alx-backend-python

# 🌀 Python Generators – Advanced Data Handling

## 📚 Project Overview

This project explores advanced use of **Python generators** to handle large datasets efficiently. Through memory-optimized, lazy-loading techniques and real-world database operations, it demonstrates how Python’s `yield` keyword can streamline data processing in modern applications.

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


## 🗂️ Directory Structure

alx-backend-python/
└── python-generators-0x00/
├── seed.py
├── 0-stream_users.py
├── 1-batch_processing.py
├── 2-lazy_paginate.py
├── 3-main.py
├── 4-stream_ages.py
├── user_data.csv
└── README.md

yaml
Copy
Edit

---

## 📌 Tasks Breakdown

### 0. Getting Started with Python Generators  
**File:** `seed.py`  
- Connect to MySQL and create `ALX_prodev` database  
- Create `user_data` table with fields: `user_id`, `name`, `email`, `age`  
- Load data from `user_data.csv`

---

### 1. Stream Users One by One  
**File:** `0-stream_users.py`  
- Function: `def stream_users()`  
- Use a generator to yield user records one at a time  
- Only 1 loop allowed

---

### 2. Batch Processing Large Data  
**File:** `1-batch_processing.py`  
- Functions:  
  - `stream_users_in_batches(batch_size)`  
  - `batch_processing(batch_size)`  
- Fetch and filter users over age 25  
- Use `yield` and no more than 3 loops

---

### 3. Lazy Loading with Pagination  
**File:** `2-lazy_paginate.py`  
- Function: `lazy_pagination(page_size)`  
- Includes `paginate_users(page_size, offset)` helper  
- Uses `yield` and just 1 loop

---

### 4. Memory-Efficient Aggregation  
**File:** `4-stream_ages.py`  
- Function: `stream_user_ages()` yields each age  
- Function: `compute_average_age()` calculates average  
- No SQL `AVG()` allowed  
- No more than 2 loops

---

## ✅ Example Output

```bash
Average age of users: 47.25
🧪 Testing Scripts
Each main test file is named like N-main.py, for example:

bash
Copy
Edit
python3 2-main.py
./3-main.py
Use head, tail, or islice() in your test scripts to limit the output when streaming large results.

✅ Final Notes
Ensure your MySQL server is running

Replace your credentials (username/password) in each script as needed

Always close your DB connections in a finally block