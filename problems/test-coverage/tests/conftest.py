import pytest
import os
import tempfile


@pytest.fixture
def sample_records():
    return [
        {"name": "Alice", "age": 30, "salary": 50000, "department": "Engineering"},
        {"name": "Bob", "age": 25, "salary": 45000, "department": "Marketing"},
        {"name": "Charlie", "age": 35, "salary": 60000, "department": "Engineering"},
        {"name": "Diana", "age": 28, "salary": 55000, "department": "Marketing"},
        {"name": "Eve", "age": 32, "salary": 52000, "department": "Engineering"},
    ]


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d
