#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=/app
python -c "import flask, pytest" 2>/dev/null || pip install flask pytest -q --root-user-action=ignore 2>/dev/null

run_suite() {
    local dir="$1" label="$2"
    echo "=== $label ==="
    output=$(python -m pytest "$dir" --tb=no -q 2>&1) || true
    passed=$(echo "$output" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+') || passed=0
    failed=$(echo "$output" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+') || failed=0
    errors=$(echo "$output" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+') || errors=0
    total=$((passed + failed + errors))
    echo "Passed: ${passed}/${total}"
}

run_suite "tests/test_public.py" "Public Tests"
echo ""
run_suite "tests/test_hidden.py" "Hidden Tests"
