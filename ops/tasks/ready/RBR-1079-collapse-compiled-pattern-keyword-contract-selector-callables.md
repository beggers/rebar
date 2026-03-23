## RBR-1079: Collapse compiled-pattern keyword contract selector callables

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining callable-selector wrapper layer in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` for the compiled-pattern module-helper keyword contract surface so the precomputed workload tuples flow directly into the contract carriers and nearby parametrized tests instead of bouncing through `partial(tuple, ...)` and two one-purpose param-builder helpers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these one-purpose param-builder helpers:
  - `_compiled_pattern_module_helper_keyword_contract_surface_params`
  - `_compiled_pattern_module_helper_keyword_contract_source_workload_params`
- `_CompiledPatternModuleHelperKeywordContractSurface` no longer stores eager workload tuples behind callable selector fields, and `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES` no longer wraps the already-materialized source workload tuples with `partial(tuple, ...)`.
- Rewire these existing consumers so they read directly from the contract surfaces or a strictly smaller same-file equivalent instead of the deleted helper/callable layer:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads`
  - `test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing`
- Keep the live contract surface intact after the cleanup:
  - the `success` surface still uses the exact ordered workload ids from `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS`;
  - the `success` precompile subset still uses the exact ordered workload ids from `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS`;
  - the `keyword-error` surface still uses the exact ordered workload ids from `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`;
  - the same contract filenames, payload round-trip assertions, callback-result expectations, probe coverage, and precompile-first call assertions remain in force for both surfaces; and
  - `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements` continues to read the same success workload surface.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements'`
- `bash -lc "! rg -n -e '^def _compiled_pattern_module_helper_keyword_contract_surface_params\\(' -e '^def _compiled_pattern_module_helper_keyword_contract_source_workload_params\\(' -e 'source_workload_selector:' -e 'precompile_source_workload_selector:' -e 'source_workload_selector=partial\\(' -e 'precompile_source_workload_selector=partial\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the callable selector and param-builder layer over introducing another support helper, registry object, or detached selector abstraction.
- Keep the existing workload ids, ordering, contract filenames, payload semantics, and callback/probe behavior intact.
- Reuse the already-materialized workload tuples as the ownership surface; do not reintroduce lazy wrappers around those same tuples under a different name.

## Notes
- `RBR-1079` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1078`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1079` task file; and
  - `rg -n 'RBR-1079|RBR-1080|RBR-1081' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'source_workload_selector: Callable|precompile_source_workload_selector: Callable|source_workload_selector=partial\\(|precompile_source_workload_selector=partial\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the callable field declarations at lines `15566-15567` and the eager `partial(tuple, ...)` wrappers at lines `15938`, `15942`, and `15950` in this run; and
  - `rg -n '^def (_compiled_pattern_module_helper_keyword_contract_surface_params|_compiled_pattern_module_helper_keyword_contract_source_workload_params)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the two dedicated param-builder helpers at lines `15958` and `15965` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements'` returned `69 passed, 653 deselected` in this run.
