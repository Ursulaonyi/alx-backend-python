# alx-backend-python

This folder contains solutions and tests for the ALX Backend Python projects, focusing on unit and integration testing, including:

- Parameterized unit tests for nested map access
- Mocking techniques
- Testing with unittest framework
- Testing decorators and network calls

## How to run tests

1. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run tests:
    ```bash
    python3 -m unittest discover
    ```

## About the tests

The `test_utils.py` file contains unit tests for the `utils.py` module, including parameterized tests for nested map access, exception handling, and plans for testing network calls and memoization.

## Folder Structure

alx-backend-python/
├── 0x03-Unittests_and_integration_tests/
│   ├── test_utils.py
│   └── utils.py
├── requirements.txt
└── README.md

