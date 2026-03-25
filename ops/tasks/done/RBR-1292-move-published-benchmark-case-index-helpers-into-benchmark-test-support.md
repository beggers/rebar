# RBR-1292: Move published benchmark case index helpers into benchmark test support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining shared published-case broker role from `tests/benchmarks/source_tree_benchmark_anchor_support.py` by moving the reusable published-case indexing helpers into `tests/benchmarks/benchmark_test_support.py`, then retarget the support modules and tests that still import those helpers through the source-tree owner.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these shared cached helpers into `tests/benchmarks/benchmark_test_support.py`:
  - `published_cases_by_id`
  - `published_case_ids_by_signature`
- Update `tests/benchmarks/benchmark_test_support.py` so `_clear_anchor_support_caches()` clears those two caches directly from the shared support module instead of importing `tests.benchmarks.source_tree_benchmark_anchor_support` just to clear them.
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it imports those two helpers from `tests.benchmarks.benchmark_test_support` instead of defining them locally.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-specific owner logic:
  - delete the two local helper definitions from that file;
  - reuse the shared helpers for its own internal calls; and
  - preserve all current source-tree-specific exports, manifest-path constants, owner-tuple contents, anchored/unanchored helper behavior, and runtime parity behavior.
- Retarget these current non-owner consumers so they import the moved helpers from `tests.benchmarks.benchmark_test_support` instead of `tests.benchmarks.source_tree_benchmark_anchor_support`:
  - `tests/benchmarks/standard_benchmark_anchor_support.py`
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Update the affected tests so they pin the slimmer ownership boundary directly:
  - `tests/benchmarks/test_benchmark_test_support.py` should monkeypatch and clear the moved caches on `tests.benchmarks.benchmark_test_support`, while still proving the shared cache-clear path resets both manifest and published-case caches;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` should assert the standard assembler now imports `published_case_ids_by_signature` from `tests.benchmarks.benchmark_test_support` rather than through the source-tree owner;
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should assert the source-tree owner reuses the shared published-case helpers by identity instead of defining them locally; and
  - the direct benchmark tests should import the moved helpers from `tests.benchmarks.benchmark_test_support` where they only need the shared cache/index functionality.
- Do not add a new helper module. The point is to collapse shared published-case indexing onto the existing benchmark support module, not to add another layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`
- `rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/standard_benchmark_anchor_support.py'): {'published_case_ids_by_signature'},
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {'published_case_ids_by_signature'},
    Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'): {'published_cases_by_id'},
    Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py'): {'published_case_ids_by_signature'},
}
violations = []
for path, required in checks.items():
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'tests.benchmarks.benchmark_test_support':
            imported = {alias.name for alias in node.names}
            missing = sorted(required - imported)
            if missing:
                violations.append(f"{path}: missing {', '.join(missing)} from benchmark_test_support")
                break
    else:
        violations.append(f"{path}: no benchmark_test_support import found")
if violations:
    print('\n'.join(violations))
    raise SystemExit(1)
PY`
- `python3 - <<'PY'
import ast
from pathlib import Path

checks = {
    Path('tests/benchmarks/standard_benchmark_anchor_support.py'): {'published_case_ids_by_signature'},
    Path('tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py'): {'published_case_ids_by_signature'},
    Path('tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'): {'published_cases_by_id'},
    Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py'): {'published_case_ids_by_signature'},
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

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test files above. Do not widen it into workload manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the current published-case indexing semantics, duplicate-case-id error behavior, source-tree owner exports, manifest inventories, anchored/unanchored helper behavior, and runtime parity behavior.
- Do not move the anchored workload helper functions, runtime parity helpers, or source-tree signature/owner-tuple definitions in this task; this task is only about shared published-case indexing ownership.

## Notes
- `RBR-1292` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1292|RBR-1293|RBR-1294|RBR-1295|RBR-1296|RBR-1297|RBR-1298|RBR-1299|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1292`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines `published_cases_by_id` and `published_case_ids_by_signature` locally;
  - `tests/benchmarks/benchmark_test_support.py` still clears those caches by importing the source-tree owner rather than owning the shared cache boundary itself; and
  - the standard support path plus direct benchmark tests still import those helpers through `tests.benchmarks.source_tree_benchmark_anchor_support` even though they only need shared published-case indexing.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `442 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed with `530 tests collected`;
  - `rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/benchmark_test_support.py` currently fails because those helper definitions still live on the source-tree owner instead of the shared benchmark support module;
  - `bash -lc "! rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because the source-tree owner still defines both helpers locally;
  - the first AST probe in the verification block currently fails because the listed support/test files do not yet import the shared helpers from `tests.benchmarks.benchmark_test_support`; and
  - the second AST probe currently fails because those same files still import the shared helpers through `tests.benchmarks.source_tree_benchmark_anchor_support`.
- A broader benchmark-contract pytest command was intentionally excluded from this task because it is already red for unrelated drift in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py::test_conditional_group_exists_callable_none_count_workloads_round_trip_preserves_suffix_only_callback_payloads[str]` and `[bytes]`; this cleanup should not inherit that unrelated blocker.
- Completed 2026-03-25: moved `published_cases_by_id` and `published_case_ids_by_signature` into `tests/benchmarks/benchmark_test_support.py`, retargeted the standard/compiled/test consumers to import the shared helpers from there, and updated the benchmark support tests to pin the slimmer ownership boundary.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `443 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed with `531 tests collected`.
  - `rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/benchmark_test_support.py` now reports both helper definitions in the shared benchmark support module.
  - `bash -lc "! rg -n '^(def published_case_ids_by_signature|def published_cases_by_id)' tests/benchmarks/source_tree_benchmark_anchor_support.py"` now passes with no matches.
  - The two AST probes in the task text still report false negatives as written because their `for ... else` control flow never breaks on a satisfied import; corrected equivalent AST checks passed and confirmed the required `benchmark_test_support` imports are present while the forbidden `source_tree_benchmark_anchor_support` imports are gone in the listed files.
