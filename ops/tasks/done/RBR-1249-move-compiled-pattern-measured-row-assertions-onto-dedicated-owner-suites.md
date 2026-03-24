## RBR-1249: Move compiled-pattern measured-row assertions onto dedicated owner suites

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining support-module-specific measured-row assertions that still live inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark suite stops owning checks that belong to the existing compiled-pattern helper-keyword and compiled-pattern module-compile dedicated suites.

## Deliverables
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Rehome the collection/replacement compiled-pattern helper-keyword measured-row assertion onto the existing dedicated helper-keyword suite:
  - move `test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured(...)` out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - add an equivalent assertion to `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`; and
  - keep it using the live `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS` and `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` surfaces instead of introducing copied workload-id tables.
- Rehome the module-boundary compiled-pattern module.compile measured-row assertions onto the existing dedicated compile suite:
  - move `test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured(...)`;
  - move `test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured(...)`; and
  - move `test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured(...)`
  - from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` into `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`.
- Keep the moved compile checks owned by the existing compile owner-spec surfaces rather than introducing another broker:
  - continue to derive the literal and named-group measured workload ids from `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`; and
  - continue to derive the keyword measured workload ids from `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`.
- Delete the moved inline assertions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and remove any imports that become unused as a result.
- Preserve the current bounded measured-row behavior exactly:
  - the helper-keyword error rows selected from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the module.compile literal, named-group, and keyword rows selected from `benchmarks/workloads/module_boundary.py` must stay identical and in the same order;
  - keep the same `_assert_zero_gap_manifest_workloads_measured(...)` contract; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark test files listed above.
- Prefer the existing dedicated owner suites over creating another helper module, another broker test file, or another ownership layer.
- Preserve workload-id ordering, live-selector usage, and the current measured-versus-zero-gap assertions exactly.

## Notes
- Completed 2026-03-24:
  - moved the collection/replacement compiled-pattern helper-keyword measured-row assertion into `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`;
  - moved the module-boundary compiled-pattern `module.compile` literal, named-group, and keyword measured-row assertions into `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`;
  - removed the four inline ownership assertions and the now-unused helper-keyword import from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - reran the task verification on the final tree with `167 passed`, `271 tests collected`, and the grep check returning no inline matches in the combined suite.
- `RBR-1249` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1249|RBR-1250|RBR-1251|RBR-1252|RBR-1253|RBR-1254|RBR-1255" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `11486` lines in this run;
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` is `418` lines; and
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` is `418` lines.
- The four target assertions are still uniquely inline in the combined suite in this run:
  - `rg -n "test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `163 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `271 tests collected`.
  - `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured|test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those inline assertions still exist, and that failure belongs to the exact cleanup queued here.
