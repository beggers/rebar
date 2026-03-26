## RBR-1343: Move source-tree compiled-pattern success owner surface onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only compiled-pattern success owner-spec data block from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops owning owner-specific selector/spec payloads and `tests/benchmarks/source_tree_benchmark_anchor_support.py` becomes the only owner for that source-tree success-contract surface.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only compiled-pattern success owner-spec data block out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`. Keep this bounded to the live success owner-spec surface:
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
- Leave genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py` alone:
  - do not widen into moving `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`, `include_live_compiled_pattern_module_success_workload(...)`, or other shared selector/signature helpers in the same task
  - if a remaining shared helper needs the moved owner specs, route it through the existing `source_tree_support` import instead of recreating another local alias block or wrapper layer
- Update the live consumers so they read the moved owner-spec surface directly from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of the generic support module:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
- Tighten the ownership checks so this split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the moved success owner-spec names are defined on the source-tree owner module, not merely re-exported from `benchmark_test_support`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces that moved success owner-spec block
- Keep the cleanup structural only:
  - do not change benchmark manifest contents, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not add a new helper module, alias shim, or wrapper layer

## Verification
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_owner_specs_pin_live_source_workload_ids tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_source_workload_params_follow_owner_specs`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the source-tree compiled-pattern success owner-spec surface that still lives in the generic benchmark support module.
- Prefer moving the existing owner-specific data block onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over recreating it behind another wrapper or generic helper.

## Notes
- `RBR-1343` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1343|RBR-1344|RBR-1345|RBR-1346' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the success owner-spec block still defined in `tests/benchmarks/benchmark_test_support.py` while `tests/benchmarks/source_tree_benchmark_anchor_support.py` still carries the matching owner-surface aliases
  - `tests/benchmarks/test_benchmark_manifest_validation.py` still consumes the grouped owner-spec tuple through `benchmark_test_support`, while the source-tree owner tests and combined suite already route the same success-contract surface through `source_tree_support`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing` passed with `39 passed in 0.19s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py::test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation` passed with `2 passed in 0.15s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_owner_specs_pin_live_source_workload_ids tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_compiled_pattern_module_success_source_workload_params_follow_owner_specs` passed with `5 passed in 0.09s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because that source-tree-only owner-spec block still lives in the generic support module, and that failure belongs exactly to this cleanup
