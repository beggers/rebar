## RBR-1344: Move source-tree compiled-pattern module compile owner surface onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only compiled-pattern module compile owner-surface block from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops owning source-tree compile owner specs, derived contract cases, and anchor lanes that already belong to `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only compiled-pattern module compile owner-surface assignments out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Keep genuinely shared compile-contract machinery in `tests/benchmarks/benchmark_test_support.py`:
  - do not widen into moving `CompiledPatternModuleCompileContractCase`, `_CompiledPatternModuleContractAnchorLane`, `_CompiledPatternModuleCompileKeywordOwnerSpec`, `_CompiledPatternModuleCompileSuccessOwnerSpec`, `build_compiled_pattern_module_compile_contract_cases(...)`, `build_compiled_pattern_module_compile_contract_source_workload_params(...)`, `build_compiled_pattern_module_contract_anchor_lanes(...)`, or shared route/signature helpers in the same task
  - if the moved owner surface still needs shared builders or classes, build it from the existing shared helpers instead of adding another alias shim or wrapper layer
- Update the remaining live consumers so they read that owner surface from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of `tests.benchmarks.benchmark_test_support`:
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
  - any remaining compile-owner checks in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Tighten the ownership checks so this split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the moved compile owner-surface names are defined on the source-tree owner module, not merely re-exported from `benchmark_test_support`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces that moved compile owner-surface block
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add a new helper module, alias shim, or wrapper layer

## Verification
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_anchor_and_case_metadata_stay_pinned_to_live_rows tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_contract_callbacks_precompile_first_argument_before_timing`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_compile_keyword_payload_round_trip_preserves_keyword_signature_type`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py::test_compiled_pattern_module_compile_standard_benchmark_definitions_are_support_owned_and_wrapper_free tests/benchmarks/test_benchmark_test_support.py::test_compiled_pattern_module_compile_surviving_suites_import_shared_support_exports tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_contract_builder_consumers_route_owner_surface_through_package_alias`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the compiled-pattern module compile owner-surface constants and their direct consumers.
- Prefer moving the existing owner-specific assignments onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over rebuilding the same surface behind another wrapper.

## Notes
- `RBR-1344` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1344|RBR-1345|RBR-1346|RBR-1347' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py` shows the compile owner-surface block still defined in `tests/benchmarks/benchmark_test_support.py` while `tests/benchmarks/source_tree_benchmark_anchor_support.py` still carries the matching alias surface
  - `tests/benchmarks/test_benchmark_manifest_validation.py` still consumes `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` through `benchmark_test_support`, while the combined source-tree suite already routes the same owner surface through `source_tree_support`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases` passed with `39 passed in 0.12s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_anchor_and_case_metadata_stay_pinned_to_live_rows tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_compile_contract_callbacks_precompile_first_argument_before_timing` passed with `17 passed in 0.10s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_compile_keyword_payload_round_trip_preserves_keyword_signature_type` passed with `8 passed in 0.17s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py::test_compiled_pattern_module_compile_standard_benchmark_definitions_are_support_owned_and_wrapper_free tests/benchmarks/test_benchmark_test_support.py::test_compiled_pattern_module_compile_surviving_suites_import_shared_support_exports tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_contract_builder_consumers_route_owner_surface_through_package_alias` passed with `6 passed in 0.27s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because that source-tree-only compile owner-surface block still lives in the generic support module, and that failure belongs exactly to this cleanup
