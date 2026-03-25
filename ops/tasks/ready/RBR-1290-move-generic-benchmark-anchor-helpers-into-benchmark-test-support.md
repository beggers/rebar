# RBR-1290: Move generic benchmark anchor helpers into benchmark test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining generic-helper broker role from `tests/benchmarks/source_tree_benchmark_anchor_support.py` by moving the shared anchor/signature helper functions into `tests/benchmarks/benchmark_test_support.py`, then retarget the benchmark-support modules and tests that still import those helpers through the source-tree owner.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/compile_proxy_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compile_proxy_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these generic helpers into `tests/benchmarks/benchmark_test_support.py`:
  - `freeze_signature_value`
  - `_definition_anchor_expectations`
  - `_workload_case_pairs_workload_ids`
  - `_workload_case_pairs_case_ids`
  - `_workload_case_pair_anchor_expectations`
- Update the benchmark-support modules that currently reach into `tests/benchmarks/source_tree_benchmark_anchor_support.py` for those helpers so they import them from `tests/benchmarks/benchmark_test_support.py` instead:
  - `tests/benchmarks/standard_benchmark_anchor_support.py`
  - `tests/benchmarks/compile_proxy_benchmark_support.py`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` structurally focused on source-tree-specific owner logic:
  - delete the five helper definitions from that file;
  - import those helpers from `tests/benchmarks/benchmark_test_support.py` for its own internal use; and
  - preserve all current source-tree-specific exports, signature behavior, owner-tuple contents, manifest-path constants, anchored/unanchored helpers, and runtime helper behavior.
- Update the affected tests so they pin the slimmer ownership boundary directly:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should assert the consumer modules now reuse the `benchmark_test_support` helper functions instead of source-tree-local definitions, while still proving those modules do not redefine the helpers locally;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` should assert the standard assembler no longer imports the generic helper names from `tests.benchmarks.source_tree_benchmark_anchor_support`;
  - `tests/benchmarks/test_compile_proxy_benchmark_support.py` should import `_definition_anchor_expectations` from `tests.benchmarks.benchmark_test_support`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` should stop importing `_definition_anchor_expectations` and `_workload_case_pair_anchor_expectations` from `tests.benchmarks.standard_benchmark_anchor_support`, and instead import them directly from `tests.benchmarks.benchmark_test_support`.
- Do not introduce a new helper broker module. The point is to collapse generic helper ownership onto the existing shared benchmark test-support module, not to add another layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def (freeze_signature_value|_definition_anchor_expectations|_workload_case_pairs_workload_ids|_workload_case_pairs_case_ids|_workload_case_pair_anchor_expectations)' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/standard_benchmark_anchor_support.py'): {
        '_definition_anchor_expectations',
        '_workload_case_pair_anchor_expectations',
        '_workload_case_pairs_case_ids',
        '_workload_case_pairs_workload_ids',
    },
    Path('tests/benchmarks/compile_proxy_benchmark_support.py'): {
        '_definition_anchor_expectations',
    },
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {
        '_definition_anchor_expectations',
        '_workload_case_pair_anchor_expectations',
    },
    Path('tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py'): {
        'freeze_signature_value',
    },
    Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py'): {
        '_definition_anchor_expectations',
        '_workload_case_pair_anchor_expectations',
        '_workload_case_pairs_case_ids',
        '_workload_case_pairs_workload_ids',
        'freeze_signature_value',
    },
    Path('tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'): {
        '_definition_anchor_expectations',
        'freeze_signature_value',
    },
    Path('tests/benchmarks/test_compile_proxy_benchmark_support.py'): {
        '_definition_anchor_expectations',
    },
}
violations = []
for path, forbidden in checks.items():
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.source_tree_benchmark_anchor_support':
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
forbidden = {'_definition_anchor_expectations', '_workload_case_pair_anchor_expectations'}
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
- Keep this cleanup structural and bounded to the support/test files above. Do not widen it into workload manifests, benchmark runner code, scorecard generation, published reports, README text, or tracked `ops/state/` prose.
- Preserve all existing benchmark definition names, manifest inventories, workload selectors, anchored case mappings, callback-parity flags, special-unanchored behavior, and live runtime helper behavior.
- Do not move source-tree-specific helpers like `published_case_ids_by_signature`, `anchored_workload_case_ids`, `unanchored_workload_ids`, `run_benchmark_workload_with_cpython`, or `assert_benchmark_workload_matches_expected_result` off the source-tree owner in this task.

## Notes
- `RBR-1290` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1290|RBR-1291|RBR-1292|RBR-1293|RBR-1294|RBR-1295|RBR-1296|RBR-1297|RBR-1298|RBR-1299|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1290`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines the five generic helper functions listed above;
  - multiple benchmark-support modules still import those helpers from `tests.benchmarks.source_tree_benchmark_anchor_support` even though `tests/benchmarks/benchmark_test_support.py` is already the repo's shared benchmark utility module; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still imports two of those helpers indirectly from `tests.benchmarks.standard_benchmark_anchor_support`, leaving the central assembler as an extra helper broker in tests.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `40 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `465 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `593 tests collected`;
  - `bash -lc "! rg -n '^def (freeze_signature_value|_definition_anchor_expectations|_workload_case_pairs_workload_ids|_workload_case_pairs_case_ids|_workload_case_pair_anchor_expectations)' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those helper definitions still live in the source-tree owner; 
  - the first `python3` AST probe in the verification section currently fails because the listed support modules and `tests/benchmarks/test_compile_proxy_benchmark_support.py` still import the generic helper names from `tests.benchmarks.source_tree_benchmark_anchor_support`; and
  - the second `python3` AST probe currently fails because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still imports `_definition_anchor_expectations` and `_workload_case_pair_anchor_expectations` from `tests.benchmarks.standard_benchmark_anchor_support`.
