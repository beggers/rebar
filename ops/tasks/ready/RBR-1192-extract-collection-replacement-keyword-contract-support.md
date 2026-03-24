# RBR-1192: Extract collection-replacement keyword contract support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining collection-replacement keyword materialization and keyword-error contract support that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded module/pattern helper support into one dedicated support module, so the giant combined benchmark suite stops owning another private callback-contract layer.

## Deliverables
- `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py` for the collection-replacement keyword-contract surface that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call`;
  - move `_pattern_helper_collection_replacement_keyword_error_workload`;
  - move `_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS`;
  - move `_is_collection_replacement_pattern_helper_keyword_error_workload`;
  - move `_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`;
  - move `_assert_keyword_error_workload_probe_measured`;
  - move `_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS`;
  - move `_is_collection_replacement_module_helper_keyword_error_workload`; and
  - move `_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`.
- Keep that extracted support pinned to the current live collection-replacement keyword-contract surface instead of widening it:
  - preserve the current pattern-helper keyword-error workload-id tuple exactly, including the bounded `pattern.split` / `pattern.sub` / `pattern.subn` rows and the current `warm` / `str` / `bytes` mix;
  - preserve the current module-helper collection-replacement keyword-error workload-id set exactly, including the bounded `module.split` / `module.sub` / `module.subn` rows and the current `purged` / `warm` mix;
  - preserve the current synthetic pattern-helper workload builder shape, including manifest id, `timing_scope`, keyword payload handling, and expected-exception round-trip behavior;
  - keep the shared probe helper limited to the current keyword-error round-trip and measured-probe assertions instead of widening it into general workload-probe coverage; and
  - keep the extracted module limited to this collection-replacement keyword-contract surface rather than absorbing module keyword-flags materialization, compiled-pattern helper contracts, wrong-text-model ownership, or unrelated grouped/conditional anchor helpers.
- Delete the duplicated inline support block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving aliases or wrapper passthroughs behind.
- Add one focused support test file at `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` that pins the moved support without depending on the full giant-suite layout:
  - cover the synthetic pattern-helper keyword-error workload builder shape;
  - cover one pattern-helper keyword-error selector case that stays in scope;
  - cover one module-helper collection-replacement keyword-error selector case that stays in scope; and
  - cover the shared probe helper on one real keyword-error source workload.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved support instead of defining that block inline:
  - keep `test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`;
  - keep `test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions`;
  - keep `test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads`;
  - keep `test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`;
  - keep `test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions`; and
  - keep `test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads`
    on the same bounded workload selections and assertions after the extraction.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark manifests, correctness fixtures, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_error_workload_probe_measured or materialize_at_callback_time or keyword_error_callbacks_match_cpython_exceptions'`

## Constraints
- Keep this cleanup structural and limited to the collection-replacement keyword-contract extraction above. Do not widen it into broader collection-replacement rewrites, new benchmark features, or a general breakup of the combined suite.
- Prefer one ordinary support module plus one focused support test file over another test-to-test import or another block of private inline helpers.
- Do not leave duplicate workload-id sets, source-workload tuples, or callback-contract helpers behind in the combined suite.

## Notes
- `RBR-1192` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1192|RBR-1193|RBR-1194|RBR-1195|RBR-1196|RBR-1197|RBR-1198|RBR-1199|RBR-1200" ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is still concrete and bounded in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still the giant benchmark suite at `17836` lines in this run;
  - `rg -n "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call|_pattern_helper_collection_replacement_keyword_error_workload|_is_collection_replacement_pattern_helper_keyword_error_workload|_assert_keyword_error_workload_probe_measured|_is_collection_replacement_module_helper_keyword_error_workload" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the support block still living inline at lines `14525`, `14554`, `14608`, `14992`, and `15476`; and
  - no repo-local support module currently owns this exact bounded keyword-contract surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, which belongs to the exact cleanup queued here.
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_error_workload_probe_measured or materialize_at_callback_time or keyword_error_callbacks_match_cpython_exceptions'` returned `78 passed, 518 deselected` in this run.
