"""Hidden test suite — gold-standard coverage tests for data_processor.py."""

import json
import os
import pytest

from src.data_processor import (
    DataValidator,
    DataTransformer,
    DataExporter,
    parse_csv,
    merge_datasets,
    deduplicate,
)


# ---------------------------------------------------------------------------
# DataValidator
# ---------------------------------------------------------------------------

class TestDataValidator:
    def _make_validator(self, schema=None):
        if schema is None:
            schema = {
                "name": {"type": "string", "required": True, "min_length": 1, "max_length": 50},
                "age": {"type": "integer", "required": True, "min": 0, "max": 150},
                "email": {"type": "email", "required": False},
                "active": {"type": "boolean", "required": False},
            }
        return DataValidator(schema)

    def test_valid_record(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice", "age": 30})
        assert ok is True
        assert errs == []

    def test_missing_required_field(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice"})
        assert ok is False
        assert any("age" in e for e in errs)

    def test_type_mismatch_integer_given_string(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice", "age": "thirty"})
        assert ok is False
        assert any("integer" in e for e in errs)

    def test_min_max_violation(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice", "age": -5})
        assert ok is False
        assert any(">=" in e for e in errs)

        ok2, errs2 = v.validate({"name": "Alice", "age": 200})
        assert ok2 is False
        assert any("<=" in e for e in errs2)

    def test_string_length_validation(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "", "age": 25})
        assert ok is False
        assert any("at least" in e for e in errs)

        ok2, errs2 = v.validate({"name": "A" * 51, "age": 25})
        assert ok2 is False
        assert any("at most" in e for e in errs2)

    def test_email_format(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice", "age": 30, "email": "bad-email"})
        assert ok is False
        assert any("email" in e.lower() for e in errs)

        ok2, errs2 = v.validate({"name": "Alice", "age": 30, "email": "alice@example.com"})
        assert ok2 is True

    def test_pattern_matching(self):
        schema = {"code": {"type": "string", "required": True, "pattern": r"^[A-Z]{3}-\d{3}$"}}
        v = DataValidator(schema)
        ok, errs = v.validate({"code": "ABC-123"})
        assert ok is True
        ok2, errs2 = v.validate({"code": "abc-123"})
        assert ok2 is False

    def test_batch_validation(self):
        v = self._make_validator()
        records = [
            {"name": "Alice", "age": 30},
            {"name": "", "age": -1},
            {"name": "Charlie", "age": 25},
        ]
        result = v.validate_batch(records)
        assert len(result["valid"]) == 2
        assert len(result["invalid"]) == 1
        assert "errors" in result["invalid"][0]

    def test_empty_schema_accepts_anything(self):
        v = DataValidator({})
        ok, errs = v.validate({"anything": "goes"})
        assert ok is True

    def test_non_dict_record(self):
        v = self._make_validator()
        ok, errs = v.validate("not a dict")
        assert ok is False
        assert any("dictionary" in e.lower() for e in errs)

    def test_invalid_schema_type(self):
        with pytest.raises(TypeError):
            DataValidator("not a dict")

    def test_batch_invalid_input(self):
        v = self._make_validator()
        with pytest.raises(TypeError):
            v.validate_batch("not a list")

    def test_boolean_type_check(self):
        v = self._make_validator()
        ok, errs = v.validate({"name": "Alice", "age": 30, "active": "yes"})
        assert ok is False
        assert any("boolean" in e for e in errs)

    def test_float_type(self):
        schema = {"score": {"type": "float", "required": True, "min": 0.0, "max": 100.0}}
        v = DataValidator(schema)
        ok, errs = v.validate({"score": 85.5})
        assert ok is True
        ok2, errs2 = v.validate({"score": "high"})
        assert ok2 is False

    def test_boolean_not_integer(self):
        """Booleans should not pass as integers."""
        schema = {"count": {"type": "integer", "required": True}}
        v = DataValidator(schema)
        ok, errs = v.validate({"count": True})
        assert ok is False


# ---------------------------------------------------------------------------
# DataTransformer
# ---------------------------------------------------------------------------

class TestDataTransformer:
    def test_normalize_basic(self, sample_records):
        t = DataTransformer()
        result = t.normalize(sample_records, ["age", "salary"])
        ages = [r["age"] for r in result]
        assert min(ages) == 0.0
        assert max(ages) == 1.0

    def test_normalize_identical_values(self):
        """When all values are the same, normalized value should be 0.0."""
        t = DataTransformer()
        records = [{"val": 5}, {"val": 5}, {"val": 5}]
        result = t.normalize(records, ["val"])
        assert all(r["val"] == 0.0 for r in result)

    def test_normalize_empty_list(self):
        t = DataTransformer()
        assert t.normalize([], ["age"]) == []

    def test_aggregate_all_functions(self, sample_records):
        t = DataTransformer()
        for func in ("sum", "avg", "min", "max", "count"):
            result = t.aggregate(sample_records, "department", "salary", func)
            assert "Engineering" in result
            assert "Marketing" in result

    def test_aggregate_invalid_function(self, sample_records):
        t = DataTransformer()
        with pytest.raises(ValueError):
            t.aggregate(sample_records, "department", "salary", "invalid")

    def test_pivot_basic(self):
        t = DataTransformer()
        records = [
            {"year": "2023", "quarter": "Q1", "revenue": 100},
            {"year": "2023", "quarter": "Q2", "revenue": 200},
            {"year": "2024", "quarter": "Q1", "revenue": 150},
        ]
        result = t.pivot(records, index="year", columns="quarter", values="revenue")
        assert result["2023"]["Q1"] == 100
        assert result["2023"]["Q2"] == 200
        assert result["2024"]["Q1"] == 150

    def test_pivot_empty(self):
        t = DataTransformer()
        assert t.pivot([], "a", "b", "c") == {}

    def test_fill_missing_constant(self):
        t = DataTransformer()
        records = [{"a": 1}, {"a": None}, {"b": 2}]
        result = t.fill_missing(records, "a", "constant", value=0)
        assert result[1]["a"] == 0
        assert result[2]["a"] == 0

    def test_fill_missing_mean(self):
        t = DataTransformer()
        records = [{"v": 10}, {"v": 20}, {"v": None}]
        result = t.fill_missing(records, "v", "mean")
        assert result[2]["v"] == 15.0

    def test_fill_missing_median(self):
        t = DataTransformer()
        records = [{"v": 10}, {"v": 20}, {"v": 30}, {"v": None}]
        result = t.fill_missing(records, "v", "median")
        assert result[3]["v"] == 20.0

    def test_fill_missing_forward_fill(self):
        t = DataTransformer()
        records = [{"v": None}, {"v": 5}, {"v": None}, {"v": None}]
        result = t.fill_missing(records, "v", "forward_fill")
        # First stays None (no previous value), rest filled from v=5
        assert result[0].get("v") is None
        assert result[1]["v"] == 5
        assert result[2]["v"] == 5
        assert result[3]["v"] == 5

    def test_fill_missing_invalid_strategy(self):
        t = DataTransformer()
        with pytest.raises(ValueError):
            t.fill_missing([{"a": 1}], "a", "bad_strategy")

    def test_fill_missing_empty(self):
        t = DataTransformer()
        assert t.fill_missing([], "a", "constant", value=0) == []

    def test_normalize_negative_numbers(self):
        t = DataTransformer()
        records = [{"v": -10}, {"v": 0}, {"v": 10}]
        result = t.normalize(records, ["v"])
        assert result[0]["v"] == 0.0
        assert result[1]["v"] == 0.5
        assert result[2]["v"] == 1.0

    def test_aggregate_empty_records(self):
        t = DataTransformer()
        result = t.aggregate([], "dept", "salary", "sum")
        assert result == {}


# ---------------------------------------------------------------------------
# DataExporter
# ---------------------------------------------------------------------------

class TestDataExporter:
    def test_to_csv_basic(self, sample_records, temp_dir):
        e = DataExporter()
        path = os.path.join(temp_dir, "out.csv")
        count = e.to_csv(sample_records, path)
        assert count == 5
        assert os.path.exists(path)

    def test_to_json_pretty(self, sample_records, temp_dir):
        e = DataExporter()
        path = os.path.join(temp_dir, "out.json")
        count = e.to_json(sample_records, path, pretty=True)
        assert count == 5
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 5
        content = open(path).read()
        assert "\n" in content  # pretty-printed

    def test_to_json_compact(self, sample_records, temp_dir):
        e = DataExporter()
        path = os.path.join(temp_dir, "out.json")
        count = e.to_json(sample_records, path, pretty=False)
        assert count == 5

    def test_summary_numeric_fields(self, sample_records):
        e = DataExporter()
        stats = e.summary(sample_records)
        assert "age" in stats
        assert "salary" in stats
        assert stats["age"]["count"] == 5
        assert stats["age"]["min"] == 25
        assert stats["age"]["max"] == 35

    def test_summary_no_numeric_fields(self):
        e = DataExporter()
        records = [{"name": "Alice"}, {"name": "Bob"}]
        stats = e.summary(records)
        assert stats == {}

    def test_summary_empty_records(self):
        e = DataExporter()
        assert e.summary([]) == {}

    def test_to_csv_empty(self, temp_dir):
        e = DataExporter()
        path = os.path.join(temp_dir, "empty.csv")
        assert e.to_csv([], path) == 0

    def test_to_json_empty(self, temp_dir):
        e = DataExporter()
        path = os.path.join(temp_dir, "empty.json")
        assert e.to_json([], path) == 0
        with open(path) as f:
            assert json.load(f) == []


# ---------------------------------------------------------------------------
# Standalone functions
# ---------------------------------------------------------------------------

class TestParseCsv:
    def test_parse_csv_with_header(self, temp_dir):
        path = os.path.join(temp_dir, "data.csv")
        with open(path, "w") as f:
            f.write("name,age,score\nAlice,30,95.5\nBob,25,88\n")
        result = parse_csv(path)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 30
        assert result[0]["score"] == 95.5

    def test_parse_csv_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_csv("/nonexistent/path.csv")

    def test_parse_csv_no_header(self, temp_dir):
        path = os.path.join(temp_dir, "raw.csv")
        with open(path, "w") as f:
            f.write("Alice,30\nBob,25\n")
        result = parse_csv(path, skip_header=False)
        assert len(result) == 2
        assert result[0]["col_0"] == "Alice"
        assert result[0]["col_1"] == 30


class TestMergeDatasets:
    def test_inner_join(self):
        left = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        right = [{"id": 1, "score": 100}, {"id": 3, "score": 80}]
        result = merge_datasets(left, right, on="id", how="inner")
        assert len(result) == 1
        assert result[0]["name"] == "A"
        assert result[0]["score"] == 100

    def test_left_join(self):
        left = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
        right = [{"id": 1, "score": 100}]
        result = merge_datasets(left, right, on="id", how="left")
        assert len(result) == 2

    def test_outer_join(self):
        left = [{"id": 1, "name": "A"}]
        right = [{"id": 2, "score": 100}]
        result = merge_datasets(left, right, on="id", how="outer")
        assert len(result) == 2

    def test_invalid_join_type(self):
        with pytest.raises(ValueError):
            merge_datasets([], [], on="id", how="cross")


class TestDeduplicate:
    def test_basic_dedup(self):
        records = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 1, "name": "C"},
        ]
        result = deduplicate(records, "id")
        assert len(result) == 2
        assert result[0]["name"] == "A"

    def test_empty_dedup(self):
        assert deduplicate([], "id") == []

    def test_missing_key_included(self):
        records = [{"id": 1}, {"name": "no_id"}, {"id": 1}]
        result = deduplicate(records, "id")
        assert len(result) == 2
