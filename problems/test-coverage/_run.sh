#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=/app
python -c "import pytest; import pytest_cov" 2>/dev/null || pip install pytest pytest-cov -q --root-user-action=ignore 2>/dev/null

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

# User's tests with coverage
echo "=== Your Tests (with Coverage) ==="
if [ -f "tests/test_solution.py" ]; then
    cov_output=$(python -m pytest tests/test_solution.py --tb=no -q --cov=src --cov-report=term-missing 2>&1) || true
    passed=$(echo "$cov_output" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+') || passed=0
    failed=$(echo "$cov_output" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+') || failed=0
    errors=$(echo "$cov_output" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+') || errors=0
    total=$((passed + failed + errors))
    echo "Tests Passed: ${passed}/${total}"
    echo ""
    cov_line=$(echo "$cov_output" | grep "TOTAL" | tail -1) || cov_line=""
    if [ -n "$cov_line" ]; then
        coverage=$(echo "$cov_line" | awk '{print $NF}')
        echo "Line Coverage: ${coverage}"
    else
        echo "Line Coverage: 0% (no tests found)"
    fi
else
    echo "No test_solution.py found. Create tests/test_solution.py to get started."
fi
echo ""

run_suite "tests/test_public.py" "Public Tests"
echo ""
run_suite "tests/test_hidden.py" "Hidden Tests"
