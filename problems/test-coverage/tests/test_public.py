"""Example tests demonstrating the API usage.

Use these as a reference for writing your own tests in tests/test_solution.py.
"""

from src.data_processor import DataValidator, DataTransformer


def test_validate_valid_record():
    """DataValidator accepts a record that matches the schema."""
    schema = {
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": True, "min": 0, "max": 150},
    }
    validator = DataValidator(schema)
    is_valid, errors = validator.validate({"name": "Alice", "age": 30})
    assert is_valid is True
    assert errors == []


def test_aggregate_sum():
    """DataTransformer.aggregate computes the sum per group."""
    records = [
        {"dept": "A", "sales": 100},
        {"dept": "B", "sales": 200},
        {"dept": "A", "sales": 150},
    ]
    transformer = DataTransformer()
    result = transformer.aggregate(records, group_by="dept", agg_field="sales", agg_func="sum")
    assert result["A"] == 250
    assert result["B"] == 200
