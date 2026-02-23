"""Data processing utilities for validation, transformation, and export."""

from __future__ import annotations

import csv
import json
import math
import os
import re
from statistics import median


class DataValidator:
    """Validates data records against a schema definition.

    Schema format:
        {
            "field_name": {
                "type": "string" | "integer" | "float" | "boolean" | "email",
                "required": True | False,
                "min": <number>,           # for integer/float
                "max": <number>,           # for integer/float
                "min_length": <int>,       # for string
                "max_length": <int>,       # for string
                "pattern": <regex_string>, # for string
            }
        }
    """

    SUPPORTED_TYPES = {"string", "integer", "float", "boolean", "email"}
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, schema: dict):
        if not isinstance(schema, dict):
            raise TypeError("Schema must be a dictionary")
        self._schema = schema

    def validate(self, record: dict) -> tuple[bool, list[str]]:
        """Validate a single record against the schema.

        Returns:
            A tuple of (is_valid, list_of_error_messages).
        """
        if not isinstance(record, dict):
            return False, ["Record must be a dictionary"]

        errors: list[str] = []

        for field_name, rules in self._schema.items():
            value = record.get(field_name)
            is_required = rules.get("required", False)

            if value is None:
                if is_required:
                    errors.append(f"Missing required field: {field_name}")
                continue

            field_type = rules.get("type", "string")
            if field_type not in self.SUPPORTED_TYPES:
                errors.append(f"Unsupported type '{field_type}' for field: {field_name}")
                continue

            type_error = self._check_type(field_name, value, field_type)
            if type_error:
                errors.append(type_error)
                continue

            errors.extend(self._check_constraints(field_name, value, rules, field_type))

        return (len(errors) == 0, errors)

    def validate_batch(self, records: list[dict]) -> dict:
        """Validate a batch of records.

        Returns:
            {"valid": [records...], "invalid": [{"record": ..., "errors": [...]}...]}
        """
        if not isinstance(records, list):
            raise TypeError("Records must be a list")

        valid: list[dict] = []
        invalid: list[dict] = []

        for record in records:
            is_valid, errors = self.validate(record)
            if is_valid:
                valid.append(record)
            else:
                invalid.append({"record": record, "errors": errors})

        return {"valid": valid, "invalid": invalid}

    def _check_type(self, field_name: str, value, field_type: str) -> str | None:
        """Check if the value matches the expected type."""
        if field_type == "string":
            if not isinstance(value, str):
                return f"Field '{field_name}' must be a string"
        elif field_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"Field '{field_name}' must be an integer"
        elif field_type == "float":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return f"Field '{field_name}' must be a number"
        elif field_type == "boolean":
            if not isinstance(value, bool):
                return f"Field '{field_name}' must be a boolean"
        elif field_type == "email":
            if not isinstance(value, str):
                return f"Field '{field_name}' must be a string"
        return None

    def _check_constraints(
        self, field_name: str, value, rules: dict, field_type: str
    ) -> list[str]:
        """Check value constraints (min, max, length, pattern, email format)."""
        errors: list[str] = []

        if field_type in ("integer", "float"):
            if "min" in rules and value < rules["min"]:
                errors.append(
                    f"Field '{field_name}' must be >= {rules['min']}"
                )
            if "max" in rules and value > rules["max"]:
                errors.append(
                    f"Field '{field_name}' must be <= {rules['max']}"
                )

        if field_type == "string":
            if "min_length" in rules and len(value) < rules["min_length"]:
                errors.append(
                    f"Field '{field_name}' must have at least {rules['min_length']} characters"
                )
            if "max_length" in rules and len(value) > rules["max_length"]:
                errors.append(
                    f"Field '{field_name}' must have at most {rules['max_length']} characters"
                )
            if "pattern" in rules:
                if not re.match(rules["pattern"], value):
                    errors.append(
                        f"Field '{field_name}' does not match pattern '{rules['pattern']}'"
                    )

        if field_type == "email":
            if not self.EMAIL_PATTERN.match(value):
                errors.append(f"Field '{field_name}' is not a valid email address")

        return errors


class DataTransformer:
    """Transforms and aggregates collections of data records."""

    def normalize(self, records: list[dict], fields: list[str]) -> list[dict]:
        """Min-max normalize specified numeric fields to [0, 1] range.

        If a field has identical values across all records, all values become 0.0.
        Non-numeric values and missing fields are left unchanged.
        """
        if not records:
            return []

        result = [dict(r) for r in records]

        for field in fields:
            values = []
            for r in result:
                v = r.get(field)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    values.append(v)

            if not values:
                continue

            min_val = min(values)
            max_val = max(values)
            val_range = max_val - min_val

            for r in result:
                v = r.get(field)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if val_range == 0:
                        r[field] = 0.0
                    else:
                        r[field] = (v - min_val) / val_range

        return result

    def aggregate(
        self,
        records: list[dict],
        group_by: str,
        agg_field: str,
        agg_func: str,
    ) -> dict:
        """Group records by a field and apply an aggregation function.

        Supported agg_func values: 'sum', 'avg', 'min', 'max', 'count'.
        Returns a dict mapping group keys to aggregated values.
        """
        valid_funcs = {"sum", "avg", "min", "max", "count"}
        if agg_func not in valid_funcs:
            raise ValueError(f"Unsupported aggregation function: {agg_func}")

        groups: dict[str, list] = {}
        for record in records:
            key = record.get(group_by)
            if key is None:
                continue
            groups.setdefault(str(key), [])
            if agg_func != "count":
                val = record.get(agg_field)
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    groups[str(key)].append(val)
            else:
                groups[str(key)].append(1)

        result: dict[str, float | int] = {}
        for key, values in groups.items():
            if not values:
                result[key] = 0
                continue

            if agg_func == "sum":
                result[key] = sum(values)
            elif agg_func == "avg":
                result[key] = sum(values) / len(values)
            elif agg_func == "min":
                result[key] = min(values)
            elif agg_func == "max":
                result[key] = max(values)
            elif agg_func == "count":
                result[key] = len(values)

        return result

    def pivot(
        self, records: list[dict], index: str, columns: str, values: str
    ) -> dict:
        """Create a pivot table from records.

        Returns a nested dict: {index_value: {column_value: aggregated_value}}.
        When multiple records share the same index+column pair, values are summed.
        """
        if not records:
            return {}

        table: dict[str, dict[str, float]] = {}
        for record in records:
            idx = record.get(index)
            col = record.get(columns)
            val = record.get(values)

            if idx is None or col is None:
                continue

            idx_str = str(idx)
            col_str = str(col)

            if idx_str not in table:
                table[idx_str] = {}

            if isinstance(val, (int, float)) and not isinstance(val, bool):
                table[idx_str][col_str] = table[idx_str].get(col_str, 0) + val
            else:
                table[idx_str].setdefault(col_str, 0)

        return table

    def fill_missing(
        self,
        records: list[dict],
        field: str,
        strategy: str,
        value=None,
    ) -> list[dict]:
        """Fill missing values in a specific field.

        Strategies:
            'constant': replace missing with the given value
            'mean': replace with the arithmetic mean of existing values
            'median': replace with the median of existing values
            'forward_fill': carry the last known value forward
        """
        valid_strategies = {"constant", "mean", "median", "forward_fill"}
        if strategy not in valid_strategies:
            raise ValueError(f"Unsupported fill strategy: {strategy}")

        if not records:
            return []

        result = [dict(r) for r in records]

        if strategy == "constant":
            for r in result:
                if field not in r or r[field] is None:
                    r[field] = value

        elif strategy in ("mean", "median"):
            existing = [
                r[field]
                for r in result
                if field in r
                and r[field] is not None
                and isinstance(r[field], (int, float))
                and not isinstance(r[field], bool)
            ]

            if not existing:
                fill_value = 0
            elif strategy == "mean":
                fill_value = sum(existing) / len(existing)
            else:
                fill_value = median(existing)

            for r in result:
                if field not in r or r[field] is None:
                    r[field] = fill_value

        elif strategy == "forward_fill":
            last_value = None
            for r in result:
                if field in r and r[field] is not None:
                    last_value = r[field]
                elif last_value is not None:
                    r[field] = last_value

        return result


class DataExporter:
    """Exports data records to files and generates summaries."""

    def to_csv(
        self, records: list[dict], filepath: str, delimiter: str = ","
    ) -> int:
        """Write records to a CSV file.

        Returns the number of data rows written (excludes header).
        """
        if not records:
            return 0

        fieldnames = list(records[0].keys())

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            for record in records:
                writer.writerow(record)

        return len(records)

    def to_json(
        self, records: list[dict], filepath: str, pretty: bool = False
    ) -> int:
        """Write records to a JSON file.

        Returns the number of records written.
        """
        if not records:
            with open(filepath, "w") as f:
                json.dump([], f)
            return 0

        with open(filepath, "w") as f:
            if pretty:
                json.dump(records, f, indent=2, ensure_ascii=False)
            else:
                json.dump(records, f, ensure_ascii=False)

        return len(records)

    def summary(self, records: list[dict]) -> dict:
        """Generate summary statistics for all numeric fields.

        Returns a dict with field names as keys and stats as values:
            {"field": {"count": N, "mean": X, "min": X, "max": X, "std": X}}
        """
        if not records:
            return {}

        numeric_fields: dict[str, list[float]] = {}
        for record in records:
            for key, val in record.items():
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    numeric_fields.setdefault(key, []).append(float(val))

        if not numeric_fields:
            return {}

        stats: dict[str, dict] = {}
        for field, values in numeric_fields.items():
            count = len(values)
            mean = sum(values) / count
            min_val = min(values)
            max_val = max(values)

            variance = sum((v - mean) ** 2 for v in values) / count
            std = math.sqrt(variance)

            stats[field] = {
                "count": count,
                "mean": round(mean, 4),
                "min": min_val,
                "max": max_val,
                "std": round(std, 4),
            }

        return stats


def parse_csv(
    filepath: str, delimiter: str = ",", skip_header: bool = True
) -> list[dict]:
    """Parse a CSV file into a list of dictionaries.

    When skip_header is True, the first row is used as field names.
    Auto-detects numeric types (int and float) for field values.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    records: list[dict] = []

    with open(filepath, "r", newline="") as f:
        if skip_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                record = {}
                for key, val in row.items():
                    record[key] = _auto_convert(val)
                records.append(record)
        else:
            reader_raw = csv.reader(f, delimiter=delimiter)
            for i, row in enumerate(reader_raw):
                record = {f"col_{j}": _auto_convert(val) for j, val in enumerate(row)}
                records.append(record)

    return records


def merge_datasets(
    left: list[dict],
    right: list[dict],
    on: str,
    how: str = "inner",
) -> list[dict]:
    """Merge two datasets on a common key field.

    Supported join types:
        'inner': only matching keys
        'left': all left records, matched right fields or None
        'outer': all records from both sides
    """
    valid_joins = {"inner", "left", "outer"}
    if how not in valid_joins:
        raise ValueError(f"Unsupported join type: {how}")

    right_index: dict[str, list[dict]] = {}
    for record in right:
        key = record.get(on)
        if key is not None:
            right_index.setdefault(str(key), []).append(record)

    result: list[dict] = []
    matched_right_keys: set[str] = set()

    for left_rec in left:
        left_key = left_rec.get(on)
        if left_key is None:
            if how in ("left", "outer"):
                result.append(dict(left_rec))
            continue

        key_str = str(left_key)
        right_matches = right_index.get(key_str, [])

        if right_matches:
            matched_right_keys.add(key_str)
            for right_rec in right_matches:
                merged = dict(left_rec)
                for k, v in right_rec.items():
                    if k != on:
                        merged[k] = v
                result.append(merged)
        elif how in ("left", "outer"):
            result.append(dict(left_rec))

    if how == "outer":
        for key_str, right_recs in right_index.items():
            if key_str not in matched_right_keys:
                for right_rec in right_recs:
                    result.append(dict(right_rec))

    return result


def deduplicate(records: list[dict], key: str) -> list[dict]:
    """Remove duplicate records based on a key field.

    Keeps the first occurrence of each unique key value.
    Records missing the key field are always included.
    """
    if not records:
        return []

    seen: set = set()
    result: list[dict] = []

    for record in records:
        val = record.get(key)
        if val is None:
            result.append(record)
            continue
        if val not in seen:
            seen.add(val)
            result.append(record)

    return result


def _auto_convert(value: str):
    """Attempt to convert a string value to int or float, else return as-is."""
    if value is None or value == "":
        return value

    try:
        int_val = int(value)
        return int_val
    except ValueError:
        pass

    try:
        float_val = float(value)
        return float_val
    except ValueError:
        pass

    return value
