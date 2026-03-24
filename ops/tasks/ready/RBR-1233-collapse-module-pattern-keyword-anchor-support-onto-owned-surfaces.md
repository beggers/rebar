## RBR-1233: Collapse module-pattern keyword anchor support onto owned surfaces

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the standalone `tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py` layer now that it only brokers two helper families between existing benchmark-support owners, so module-keyword anchor wiring lives on the shared source-tree anchor surface and pattern-window/keyword wiring lives on the existing pattern-boundary support surface instead of on a mixed extra module plus a dedicated extra test file.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete the standalone mixed bridge layer:
  - remove `tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py`; and
  - remove `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`.
- Fold the module-helper keyword selectors and signature helpers onto the shared source-tree benchmark anchor owner in `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - move `_module_workflow_keyword_correctness_case_signature(...)`;
  - move `_module_workflow_keyword_workload_args(...)`;
  - move `_module_workflow_keyword_workload_signature(...)`;
  - move `_is_module_workflow_keyword_flags_workload(...)`; and
  - move `_is_module_workflow_keyword_error_workload(...)`.
- Fold the direct-`Pattern` window and keyword selectors/signatures onto the existing pattern-boundary owner in `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`:
  - move `_pattern_window_positional_indexlike_correctness_case_signature(...)`;
  - move `_pattern_window_positional_indexlike_workload_args(...)`;
  - move `_pattern_window_positional_indexlike_workload_signature(...)`;
  - move `_is_pattern_window_positional_indexlike_workload(...)`;
  - move `_pattern_keyword_window_correctness_case_signature(...)`;
  - move `_pattern_keyword_window_workload_signature(...)`; and
  - move `_is_pattern_keyword_window_workload(...)`.
- Rehome the focused coverage from the deleted dedicated test file onto the existing owner test files instead of recreating another wrapper surface:
  - put the module-keyword selector/signature assertions into `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`;
  - put the pattern window/keyword selector/signature assertions into `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`; and
  - keep the current collection-replacement keyword-contract checks reachable from `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` without introducing a new `*_support.py` file.
- Update downstream imports to use the owner modules directly:
  - `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`;
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - any touched benchmark-support tests.
- Preserve the current bounded benchmark behavior exactly:
  - the module keyword flags/error rows on `benchmarks/workloads/module_boundary.py` stay on the existing shared source-tree anchor contract path;
  - the `Pattern.search`/`match`/`fullmatch`/`findall`/`finditer` positional-window and keyword-window rows on `benchmarks/workloads/pattern_boundary.py` stay on the existing pattern-boundary contract path; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, runtime-contract suites, reports, or new abstraction layers.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! test -e tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py && ! test -e tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py"`

## Constraints
- Keep the cleanup structural and bounded to the benchmark-support/test layer listed above. Do not modify workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops state prose.
- Prefer moving the existing helper bodies directly onto the destination owner modules over leaving compatibility aliases that only forward to another module.
- Preserve the current selector rules, signature tuple shapes, and combined-suite contract definitions exactly.

## Notes
- `RBR-1233` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the highest filed task is `RBR-1232`; and
  - `rg -n "RBR-1233|RBR-1234|RBR-1235|RBR-1236|RBR-1237" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` matched only historical mentions inside completed task files, not a live reservation in tracked planning/state surfaces.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py` still exists and is imported only by `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`, `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`;
  - the pattern-window helper already leaks through `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, so the mixed bridge is not the real owner today; and
  - the destination owner modules already exist at `tests/benchmarks/source_tree_benchmark_anchor_support.py` and `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` passed with `123 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `107 tests collected`.
  - `bash -lc "! test -e tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py && ! test -e tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py"` currently fails because both files still exist, and that failure belongs to the exact cleanup this task queues.
