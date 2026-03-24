# RBR-1214: Move collection-replacement keyword contract tests onto dedicated suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining collection-replacement keyword contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated owner in `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, so the giant combined benchmark suite stops owning another support-specific keyword/materialization surface.

## Deliverables
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` so it becomes the owner for the current collection-replacement keyword contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation`
  - `test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation`
  - `test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`
  - `test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions`
  - `test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads`
  - `test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`
  - `test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions`
  - `test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current manifest payloads, workload ids, bool-versus-int and indexlike checks, `keyword_arguments()` assertions, callback materialization field ordering, expected exception parity, and internal workload probe coverage;
  - preserve the current pytest parametrization ids and test names apart from relocating them;
  - keep the mixed `_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS` coverage intact rather than dropping the module-boundary keyword-error rows from the dedicated owner; and
  - keep using ordinary `load_manifest(...)`, `workload_from_payload(...)`, `workload_to_payload(...)`, `build_callable(...)`, `run_benchmark_workload_with_cpython(...)`, and `run_internal_workload_probe(...)` calls rather than inventing a new test-only representation.
- Reuse the existing dedicated suite instead of adding another architectural layer:
  - keep `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` as the owner for this collection-replacement keyword contract surface;
  - do not add a new `*_support.py` module or another one-off contract suite for this extraction; and
  - do not widen this cleanup into pattern-window keyword contracts, compiled-pattern helper keyword contracts, manifest-validation tests, or benchmark harness implementation code.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads'`
- `bash -lc "! rg -n 'test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation|test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation|test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions|test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads|test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions|test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1214` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run before this task was added; and
  - `rg -n "RBR-1214|RBR-1215|RBR-1216|RBR-1217|RBR-1218" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed `RBR-1212` and `RBR-1213` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `rg -n "def test_(standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation|standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation|pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions|run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads|module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions|run_internal_workload_probe_measures_module_helper_keyword_error_workloads)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently matches only the combined-suite block at lines `11847`, `12352`, `13033`, `13242`, `13327`, `13619`, `13763`, and `13807`;
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` already exists as the dedicated owner for this support surface; and
  - this task removes one misplaced contract block instead of creating a sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` returned `4 passed in 0.05s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads'` returned `88 passed, 352 deselected in 0.24s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those eight tests still live in the combined suite.

## Completion Note
- Moved the eight collection-replacement keyword contract tests into `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` and deleted the inline copies from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Kept the dedicated owner on the same live helper surface: manifest payloads, parametrization ids, callback-time materialization checks, keyword-error parity, and internal workload probe coverage all still run through the existing benchmark helpers.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` returned `92 passed in 0.18s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads'` returned `352 deselected in 0.27s`, which is the expected post-move result because those tests no longer live in the combined suite.
  - `bash -lc "! rg -n 'test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation|test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation|test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions|test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads|test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions|test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` returned success.
