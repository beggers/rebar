# RBR-1291: Move standard benchmark anchor contract types into benchmark test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining shared-type broker role from `tests/benchmarks/standard_benchmark_anchor_support.py` by moving the reusable benchmark anchor contract types into `tests/benchmarks/benchmark_test_support.py`, then retarget the owner support modules and tests that still import those types through the central assembler.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/compile_proxy_benchmark_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these shared benchmark anchor contract types into `tests/benchmarks/benchmark_test_support.py`:
  - `StandardBenchmarkAnchorContract`
  - `StandardBenchmarkAnchorContractDefinition`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so it imports those two names from `tests/benchmarks/benchmark_test_support.py` instead of defining them locally.
- Retarget every owner support module that still imports `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.standard_benchmark_anchor_support` so it imports the type from `tests.benchmarks.benchmark_test_support` instead:
  - `tests/benchmarks/compile_proxy_benchmark_support.py`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- Retarget `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.benchmark_test_support` while keeping `STANDARD_BENCHMARK_DEFINITIONS` sourced from `tests.benchmarks.standard_benchmark_anchor_support`.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` so it pins the slimmer ownership boundary directly:
  - assert the central assembler source no longer defines either contract class;
  - assert the owner support modules no longer import `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.standard_benchmark_anchor_support`; and
  - keep the existing standard-inventory object-reuse and splice-order assertions intact.
- Do not add a new benchmark support module. The point is to collapse shared contract-type ownership onto the existing `benchmark_test_support.py` module, not to create another layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'class StandardBenchmarkAnchorContract|class StandardBenchmarkAnchorContractDefinition' tests/benchmarks/standard_benchmark_anchor_support.py"`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/compile_proxy_benchmark_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
    Path('tests/benchmarks/source_tree_benchmark_anchor_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
    Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
    Path('tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
    Path('tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'): {'StandardBenchmarkAnchorContractDefinition'},
}
violations = []
for path, forbidden in checks.items():
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.standard_benchmark_anchor_support':
            imported = {alias.name for alias in node.names}
            bad = sorted(imported & forbidden)
            if bad:
                violations.append(f"{path}: {', '.join(bad)}")
if violations:
    print('\n'.join(violations))
    raise SystemExit(1)
PY`
- `python3 - <<'PY'
import ast
from pathlib import Path

path = Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py')
forbidden = {'StandardBenchmarkAnchorContractDefinition'}
tree = ast.parse(path.read_text())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.standard_benchmark_anchor_support':
        imported = {alias.name for alias in node.names}
        bad = sorted(imported & forbidden)
        if bad:
            print(f"{path}: {', '.join(bad)}")
            raise SystemExit(1)
PY`

## Constraints
- Keep this cleanup structural and bounded to the support/test files above. Do not widen it into benchmark workload manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the existing definition names, manifest inventories, anchored case mappings, workload selectors, callback-parity flags, lazy owner export behavior, and standard inventory splice order.
- Do not move the generic helper functions or central helper methods in `tests/benchmarks/standard_benchmark_anchor_support.py` during this task; this task is only about shared contract-type ownership.

## Notes
- `RBR-1291` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1291|RBR-1292|RBR-1293|RBR-1294|RBR-1295|RBR-1296|RBR-1297|RBR-1298|RBR-1299|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1291`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/standard_benchmark_anchor_support.py` still defines `StandardBenchmarkAnchorContract` and `StandardBenchmarkAnchorContractDefinition` locally;
  - six owner support modules still import `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.standard_benchmark_anchor_support`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still imports `StandardBenchmarkAnchorContractDefinition` through the central assembler even though it only needs the shared contract type.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `246 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `221 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `555 tests collected`;
  - the negative `rg` command above currently fails because `tests/benchmarks/standard_benchmark_anchor_support.py` still defines both contract classes;
  - the first AST probe above currently fails because the listed owner support modules still import `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.standard_benchmark_anchor_support`; and
  - the second AST probe above currently fails because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still imports `StandardBenchmarkAnchorContractDefinition` from `tests.benchmarks.standard_benchmark_anchor_support`.
