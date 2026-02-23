import pytest


@pytest.fixture(autouse=True)
def reset_state():
    """Reset inventory state before each test."""
    from src.inventory import init_inventory
    init_inventory()
