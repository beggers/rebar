## RBR-1255: Move collection-replacement measured-row ownership onto dedicated support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining `collection-replacement` measured-row ownership assertions that still live inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark broker stops owning checks that belong to the existing dedicated collection-replacement support surfaces.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these seven inline ownership assertions out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome equivalent checks into `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`:
  - `test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_split_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured(...)`
  - `test_collection_replacement_manifest_keeps_grouped_callable_rows_measured(...)`
- Keep the moved assertions owned by the existing collection-replacement support surfaces rather than by the combined broker:
  - continue to derive the positional-indexlike rows from `_is_collection_replacement_positional_indexlike_workload(...)`;
  - continue to derive the pattern collection rows from `_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES`;
  - continue to derive the literal replacement rows from `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES`, `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR`, and `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR`; and
  - continue to derive the grouped-callable rows from `_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS` and `_is_collection_replacement_grouped_callable_workload(...)`.
- If the dedicated suite needs the collection-replacement route/spec helpers that currently live in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, move only the minimal collection-replacement-owned definitions into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of copying workload-id inventories into the test file.
- Preserve the current bounded measured-row behavior exactly:
  - the positional-indexlike selector must keep asserting the same six workload ids in the same order;
  - the pattern collection selectors must keep asserting the same three `findall`, three `finditer`, and three `split` workload ids in the same order;
  - the literal replacement selectors must keep asserting the same 20 pattern rows and 18 module rows in the same order; and
  - the grouped-callable selector must keep asserting the same four workload ids in the same order.
- Delete the moved inline assertions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and remove any imports that become unused as a result.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured|test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_split_rows_measured|test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured|test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured|test_collection_replacement_manifest_keeps_grouped_callable_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark files listed above.
- Prefer the existing collection-replacement support suite over creating another broker test file, another helper wrapper, or another ownership layer.
- Preserve the live selector usage, workload-id ordering, and current zero-gap measured-row contract exactly.

## Notes
- `RBR-1255` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1255|RBR-1256|RBR-1257|RBR-1258|RBR-1259|RBR-1260" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `11055` lines in this run;
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `1145` lines; and
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `567` lines.
- The seven target assertions are still uniquely inline in the combined suite in this run:
  - `rg -n "test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured|test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_split_rows_measured|test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured|test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured|test_collection_replacement_manifest_keeps_grouped_callable_rows_measured" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `31 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `128 tests collected`.
  - `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured|test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_split_rows_measured|test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured|test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured|test_collection_replacement_manifest_keeps_grouped_callable_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those inline assertions still exist, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the seven collection-replacement measured-row ownership assertions into `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Rehomed the collection-replacement route and selector ownership into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, including the pattern-collection routes, literal-replacement routes/selectors, and grouped-callable workload pairs/selectors that the dedicated suite now exercises directly.
- Removed the corresponding inline ownership assertions and now-unused local route/selector definitions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `38 passed`.
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `128 tests collected`.
- `bash -lc "! rg -n 'test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured|test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured|test_collection_replacement_manifest_keeps_pattern_split_rows_measured|test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured|test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured|test_collection_replacement_manifest_keeps_grouped_callable_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.
