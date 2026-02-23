import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_data():
    """Reset all in-memory data before each test."""
    from src.app import books, users, carts, orders, next_id
    books.clear()
    users.clear()
    carts.clear()
    orders.clear()
    next_id["books"] = 1
    next_id["users"] = 1
    next_id["orders"] = 1
