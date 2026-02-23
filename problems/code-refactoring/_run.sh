#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=/app
python -c "import pytest; import radon; import ruff" 2>/dev/null || pip install pytest ruff radon -q --root-user-action=ignore 2>/dev/null

SRC="src/inventory.py"

# === Code Quality ===
echo "=== Code Quality ==="

total_lines=$(wc -l < "$SRC" | tr -d ' ')
code_lines=$(python -c "
import ast
with open('$SRC') as f:
    source = f.read()
lines = set()
tree = ast.parse(source)
for node in ast.walk(tree):
    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
        for ln in range(node.lineno, node.end_lineno + 1):
            lines.add(ln)
print(len(lines))
")
echo "Total Lines: ${total_lines}"
echo "Code Lines: ${code_lines}"

LINT_RULES="E,W,C90,N,UP,B,A,C4,SIM,PLR,PLW"
lint_output=$(python -m ruff check "$SRC" --select="$LINT_RULES" 2>&1 || true)
lint_count=$(echo "$lint_output" | grep -oE 'Found [0-9]+ errors?' | grep -oE '[0-9]+') || lint_count=0
echo "Lint Issues: ${lint_count}"

avg_cc=$(python -m radon cc "$SRC" -a -nc 2>&1 | grep "Average complexity" | grep -oE '[0-9]+\.[0-9]+') || avg_cc="0.0"
grade=$(python -c "
cc = $avg_cc
if cc <= 5: print('A')
elif cc <= 10: print('B')
elif cc <= 20: print('C')
elif cc <= 30: print('D')
else: print('F')
")
echo "Avg Complexity: ${grade} (${avg_cc})"

long_funcs=$(python -c "
import ast
with open('$SRC') as f:
    tree = ast.parse(f.read())
count = 0
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        length = node.end_lineno - node.lineno + 1
        if length > 30:
            count += 1
print(count)
")
echo "Functions over 30 lines: ${long_funcs}"

echo ""

# === Tests ===
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
