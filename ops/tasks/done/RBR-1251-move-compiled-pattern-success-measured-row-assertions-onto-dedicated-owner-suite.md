## RBR-1251: Move compiled-pattern success measured-row assertions onto dedicated owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern success measured-row assertions that still live inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark suite stops owning checks that belong to the existing dedicated compiled-pattern success support suite.

## Deliverables
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Rehome the collection/replacement compiled-pattern success measured-row assertion onto `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`:
  - move `test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured(...)` out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - add an equivalent assertion to `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` that keeps deriving the live source workload ids from the existing compiled-pattern success owner-spec surface instead of introducing copied workload-id tables.
- Rehome the three module-boundary compiled-pattern success measured-row assertions onto `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`:
  - move `test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured(...)`;
  - move `test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured(...)`; and
  - move `test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured(...)`
  - from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` into the dedicated success suite.
- Keep the moved assertions owned by the existing live success surfaces rather than another broker:
  - continue to derive the collection/replacement rows from the existing collection/replacement compiled-pattern success owner spec in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`;
  - continue to derive the module-boundary rows from the existing module-boundary compiled-pattern success owner spec and its live include selectors; and
  - do not add copied workload-id inventories, new support modules, or another ownership layer.
- Delete the moved inline assertions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and remove any imports that become unused as a result.
- Preserve the current bounded measured-row behavior exactly:
  - the collection/replacement compiled-pattern success rows selected from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the module-boundary literal, bounded-wildcard, and verbose-bytes compiled-pattern success rows selected from `benchmarks/workloads/module_boundary.py` must stay identical and in the same order; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the two benchmark test files listed above.
- Prefer the existing dedicated success suite over creating another helper module, another broker test file, or another ownership layer.
- Preserve workload-id ordering, live-selector usage, and the current measured-versus-zero-gap assertions exactly.

## Notes
- `RBR-1251` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1251|RBR-1252|RBR-1253|RBR-1254|RBR-1255|RBR-1256" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still contains the four inline compiled-pattern success measured-row assertions; and
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` already owns the corresponding compiled-pattern success owner-spec surfaces and passes as a standalone suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `41 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `145 tests collected`.
  - `rg -n "test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those inline assertions still exist, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the four compiled-pattern success measured-row assertions into `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`.
- The dedicated suite now derives expected workload ids from the existing compiled-pattern success owner specs and live include selectors, then verifies those rows stay measured in the live combined manifests.
- Removed the corresponding inline assertions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `45 passed`.
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` passed with `145 tests collected`.
- `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured|test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.
