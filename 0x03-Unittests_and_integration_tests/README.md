# 0x03 - Unittests and Integration Tests

This directory contains solutions and tests for the ALX Backend Python project focused on writing **unit tests**, **integration tests**, and applying **mocking** techniques using `unittest`, `parameterized`, and `unittest.mock`.

---

## 📦 Project Content

### Unit and Integration Tests
This project includes:
- Parameterized unit tests
- Exception handling tests
- Memoization function testing
- Integration tests using patched HTTP requests
- Use of fixtures and mocking to simulate external API behavior

---

## 📁 Folder Structure

```
alx-backend-python/
└── 0x03-Unittests_and_integration_tests/
    ├── client.py               # GitHubOrgClient logic
    ├── fixtures.py             # Payload fixture for integration tests
    ├── test_client.py          # Unit & integration tests for client.py
    ├── test_utils.py           # Unit tests for utils.py
    ├── utils.py                # Utility functions with decorators
    └── README.md               # Project description and instructions
```

---

## 🧪 How to Run Tests

1. **Create and activate a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run all tests:**
```bash
python3 -m unittest discover
```

Or run specific test files:
```bash
python3 -m unittest test_utils.py
python3 -m unittest test_client.py
```

---

## ✅ Test Descriptions

- **`test_utils.py`**:  
  Tests functions from `utils.py`, including:
  - Accessing nested maps with parameterized input
  - Exception raising
  - Memoization using decorators

- **`test_client.py`**:  
  Tests the `GithubOrgClient` class from `client.py`, including:
  - API response handling
  - Filtering repos by license
  - Integration testing using fixtures

- **`fixtures.py`**:  
  Contains JSON-style data used in integration tests to simulate GitHub API responses.

---

## 📌 Requirements

- Python 3.7+
- `parameterized`
- `requests`

Install them with:
```bash
pip install -r requirements.txt
```

---

## 🔖 Author

- [**Ursula Onyinye Okafo**](https://github.com/ursulaonyi)

Project completed as part of the ALX Backend Python track.

