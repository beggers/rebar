# RBR-1293: Move generic source-tree contract builders into benchmark test support

Status: done
Owner: architecture-implementation
Created: 2026-03-25
Completed: 2026-03-25

## Goal
- Remove the remaining shared contract-builder broker role from `tests/benchmarks/source_tree_contract_benchmark_support.py` by moving the generic manifest/workload construction helpers into `tests/benchmarks/benchmark_test_support.py`, then retarget the owner support modules and benchmark tests that still import those generic helpers through the source-tree contract module.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_contract_benchmark_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_source_tree_contract_benchmark_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`

## Acceptance Criteria
- Move these generic contract-builder definitions into `tests/benchmarks/benchmark_test_support.py`:
  - `_SourceTreeContractBuilderSpec`
  - `_source_tree_contract_manifest_payload`
  - `_source_tree_contract_workload`
  - `_source_tree_contract_manifest`
  - `_contract_source_workloads`
- Update `tests/benchmarks/source_tree_contract_benchmark_support.py` so it imports those five names from `tests.benchmarks.benchmark_test_support` instead of defining them locally.
- Keep `tests/benchmarks/source_tree_contract_benchmark_support.py` focused on the compiled-pattern-specific contract helpers it still owns:
  - delete the five local generic builder definitions from that file;
  - reuse the moved helpers for its own internal behavior where needed; and
  - preserve `COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS`, `compiled_pattern_contract_expected_build_calls`, and all current contract-build semantics and drift-check behavior.
- Retarget the current owner support modules that still import the generic builder API from `tests.benchmarks.source_tree_contract_benchmark_support` so they import those names from `tests.benchmarks.benchmark_test_support` instead:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- Retarget the benchmark tests that only need the generic builder API so they import those names from `tests.benchmarks.benchmark_test_support` instead of `tests.benchmarks.source_tree_contract_benchmark_support`:
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- Update `tests/benchmarks/test_source_tree_contract_benchmark_support.py` so it pins the slimmer ownership boundary directly:
  - assert `tests/benchmarks/source_tree_contract_benchmark_support.py` no longer defines the five generic builder names locally;
  - assert the source-tree contract module reuses the moved builder helpers from `tests.benchmarks.benchmark_test_support` by identity; and
  - keep the compiled-pattern-specific excluded-field and build-call assertions intact.
- Do not add a new helper broker module. The point is to collapse shared contract-builder ownership onto the existing benchmark support module, not to introduce another layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest|def _contract_source_workloads)' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest|def _contract_source_workloads)' tests/benchmarks/source_tree_contract_benchmark_support.py"`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py'): {'_SourceTreeContractBuilderSpec'},
    Path('tests/benchmarks/test_benchmark_manifest_validation.py'): {'_SourceTreeContractBuilderSpec', '_source_tree_contract_manifest'},
    Path('tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads', '_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
}
violations = []
for path, required in checks.items():
    tree = ast.parse(path.read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.benchmark_test_support':
            imported = {alias.name for alias in node.names}
            if required <= imported:
                found = True
                break
    if not found:
        violations.append(str(path))
if violations:
    print('\n'.join(violations))
    raise SystemExit(1)
PY`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/collection_replacement_benchmark_anchor_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads'},
    Path('tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py'): {'_SourceTreeContractBuilderSpec'},
    Path('tests/benchmarks/test_benchmark_manifest_validation.py'): {'_SourceTreeContractBuilderSpec', '_source_tree_contract_manifest'},
    Path('tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py'): {'_SourceTreeContractBuilderSpec', '_contract_source_workloads', '_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
    Path('tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py'): {'_source_tree_contract_manifest', '_source_tree_contract_workload'},
}
violations = []
for path, forbidden in checks.items():
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.source_tree_contract_benchmark_support':
            imported = {alias.name for alias in node.names}
            bad = sorted(imported & forbidden)
            if bad:
                violations.append(f"{path}: {', '.join(bad)}")
if violations:
    print('\n'.join(violations))
    raise SystemExit(1)
PY`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test files above. Do not widen it into benchmark workload manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the current contract-manifest payload shape, contract workload defaults, selector-order drift checks, compiled-pattern build-call expectations, and all owner-specific benchmark support behavior.
- Do not move `COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS` or `compiled_pattern_contract_expected_build_calls` off `tests/benchmarks/source_tree_contract_benchmark_support.py` in this task; this cleanup is only about the generic shared builder layer.

## Notes
- `RBR-1293` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1293|RBR-1294|RBR-1295|RBR-1296|RBR-1297|RBR-1298|RBR-1299|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1293`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_contract_benchmark_support.py` still defines the five generic builder names listed above locally;
  - four owner support modules still import `_SourceTreeContractBuilderSpec` and/or `_contract_source_workloads` from `tests.benchmarks.source_tree_contract_benchmark_support`; and
  - seven benchmark tests still import the generic contract-builder API from `tests.benchmarks.source_tree_contract_benchmark_support` even though they only need shared manifest/workload construction.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `409 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `409 tests collected`;
  - `bash -lc "! rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest|def _contract_source_workloads)' tests/benchmarks/benchmark_test_support.py"` currently fails because `benchmark_test_support.py` does not yet define those helpers;
  - `rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest|def _contract_source_workloads)' tests/benchmarks/source_tree_contract_benchmark_support.py` currently reports all five local definitions; and
  - the two AST probes above currently fail because the listed support/test files still import the generic builder API from `tests.benchmarks.source_tree_contract_benchmark_support` instead of `tests.benchmarks.benchmark_test_support`.

## Completion Note
- Moved the five generic source-tree contract builder helpers into `tests/benchmarks/benchmark_test_support.py`, slimmed `tests/benchmarks/source_tree_contract_benchmark_support.py` down to the compiled-pattern-specific contract ownership it still needs, retargeted the listed support/test imports, and updated the contract support test to assert the shared-builder boundary by identity.
- Verified with the task pytest slice and collect-only pass; the targeted suite now passes with `410 passed` and `410 tests collected`.
