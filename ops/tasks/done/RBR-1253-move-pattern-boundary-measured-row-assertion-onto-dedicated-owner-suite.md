## RBR-1253: Move pattern-boundary measured-row assertion onto dedicated owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining pattern-boundary measured-row ownership assertion that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark suite stops owning a manifest-level zero-gap check that belongs to the existing dedicated pattern-boundary owner suite.

## Deliverables
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome an equivalent assertion into `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`.
- Keep the moved assertion owned by the existing pattern-boundary support surfaces instead of introducing another broker:
  - continue to derive wrong-text-model rows from `_is_pattern_boundary_wrong_text_model_workload(...)`;
  - continue to derive bounded-wildcard rows from `_is_pattern_bounded_wildcard_workload(...)` and `_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS`;
  - continue to derive verbose-regression rows from `_is_pattern_verbose_regression_workload(...)`, `_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS`, and `_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS`;
  - continue to derive keyword-window rows from `_is_pattern_keyword_window_workload(...)`; and
  - continue to derive positional-indexlike rows from `_is_pattern_window_positional_indexlike_workload(...)`.
- Preserve the current bounded measured-row behavior exactly:
  - the moved assertion must keep verifying the same 49 measured rows in `benchmarks/workloads/pattern_boundary.py`;
  - it must keep the same concatenated measured-row ordering across the wrong-text-model, bounded-wildcard, verbose-regression, keyword-window, and positional-window slices; and
  - it must keep asserting the exact explicit workload-id tuples for the wrong-text-model, keyword-window, and positional-window selections.
- Delete the moved inline assertion from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and remove any imports that become unused as a result.
- Do not widen this cleanup into `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the two benchmark test files listed above.
- Prefer the existing dedicated pattern-boundary owner suite over creating another helper module, another broker test file, or another ownership layer.
- Preserve the current live selector usage, workload-id ordering, and zero-gap measured-row contract exactly.

## Notes
- `RBR-1253` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1253|RBR-1254|RBR-1255|RBR-1256|RBR-1257|RBR-1258" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `11264` lines in this run;
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` is `613` lines; and
  - `rg -n "test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `23 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `123 tests collected`.
  - `bash -lc "! rg -n 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because that inline assertion still exists, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the pattern-boundary measured-row assertion into `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`.
- The dedicated suite now derives the same wrong-text-model, bounded-wildcard, verbose-regression, keyword-window, and positional-window slices from the existing owner selectors and preserves the exact workload-id tuples and concatenated measured-row ordering for the 49-row manifest.
- Removed the inline assertion and now-unused pattern-boundary manifest constants import from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `24 passed`.
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `123 tests collected`.
- `bash -lc "! rg -n 'test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.
