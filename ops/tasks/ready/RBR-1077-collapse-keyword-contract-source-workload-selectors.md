# RBR-1077: Collapse keyword-contract source workload selectors

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining thin keyword-contract source-workload selector wrappers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the keyword-error and compiled-pattern keyword contract checks read directly from the canonical manifest selectors or the existing shared contract-source helper instead of bouncing through five one-purpose helper names.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these thin source-workload selector wrappers:
  - `_pattern_helper_keyword_error_source_workloads`
  - `_module_helper_keyword_error_source_workloads`
  - `_compiled_pattern_module_helper_keyword_source_workloads`
  - `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads`
  - `_compiled_pattern_module_helper_keyword_error_source_workloads`
- Replace that wrapper layer with direct use of the existing ownership surfaces, or a strictly smaller same-file equivalent:
  - `_selected_manifest_workloads(...)`
  - `_contract_source_workloads(...)`
  - inline or `partial(...)`-bound selector callables wired directly into `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES` and the affected parametrized tests
- Rewire these existing consumers so they no longer depend on the deleted wrapper names:
  - `test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads`
  - `test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions`
  - `test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads`
  - `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation`
  - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_keyword_contract_workloads`
  - `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing`
- Keep the live keyword-contract surfaces intact after the cleanup:
  - the pattern-helper keyword-error slice still selects exactly `_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS` in order and still raises the same drift assertion if that source surface changes;
  - the module-helper keyword-error slice still covers the same union of module-boundary keyword-error rows plus collection/replacement keyword-error rows in the same order;
  - the compiled-pattern module-helper success slice still selects exactly `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids` in order;
  - the compiled-pattern precompile-anchor subset still selects exactly `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids` in order and still raises the same drift assertion if that anchor subset changes; and
  - the compiled-pattern keyword-error slice still selects exactly `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids` in order.
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark manifests, correctness fixtures, implementation code, reports, README copy, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_keyword_contract_workloads or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n '^def (_pattern_helper_keyword_error_source_workloads|_module_helper_keyword_error_source_workloads|_compiled_pattern_module_helper_keyword_source_workloads|_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads|_compiled_pattern_module_helper_keyword_error_source_workloads)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the five wrappers over introducing another support module, registry file, or detached selector family.
- Keep the existing workload ids, ordering, drift checks, contract filenames, anchored-case coverage, and callback/probe semantics intact.
- Reuse the already-landed `_contract_source_workloads(...)` helper where it shrinks code; do not add a parallel helper that only renames the same selections again.

## Notes
- `RBR-1077` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this file is added;
  - `ops/tasks/done/` currently runs through `RBR-1076`; and
  - `rg -n 'RBR-1077|RBR-1078|RBR-1079' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only a historical note inside `ops/tasks/done/RBR-1076-collapse-collection-replacement-workload-selector-wrappers.md`, not a live reservation or task file for `RBR-1077`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle still shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The duplication target is concrete in the live checkout:
  - `rg -n '^def (_pattern_helper_keyword_error_source_workloads|_module_helper_keyword_error_source_workloads|_compiled_pattern_module_helper_keyword_source_workloads|_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads|_compiled_pattern_module_helper_keyword_error_source_workloads)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the five wrapper definitions in this run;
  - `sed -n '14530,14575p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the pattern-helper keyword-error selection wrapper still doing nothing beyond one manifest query plus an ordered-id drift check;
  - `sed -n '15420,15540p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the module-helper and compiled-pattern keyword success wrappers still only forwarding manifest selections into parametrized tests; and
  - `sed -n '15900,15940p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the compiled-pattern keyword-error wrapper still only forwarding one manifest selection into the contract surface.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_keyword_contract_workloads or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing'` returned `77 passed, 645 deselected` in this run.
