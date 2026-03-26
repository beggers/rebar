## RBR-1341: Move source-tree helper-keyword contract surface onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only compiled-pattern helper-keyword contract data block from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops owning owner-specific selector/spec payloads and `tests/benchmarks/source_tree_benchmark_anchor_support.py` becomes the only owner for that source-tree contract surface.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only compiled-pattern helper-keyword contract data block out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`. Keep this bounded to the live helper-keyword block in the generic module:
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS`
  - `_is_collection_replacement_compiled_pattern_keyword_error_workload`
- Leave genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py` alone:
  - do not widen into moving `compiled_pattern_contract_expected_build_calls(...)`, `_compiled_pattern_module_helper_route(...)`, or unrelated collection/pattern-boundary helpers in the same task
  - route the moved block through existing shared primitives rather than inventing a new abstraction layer
- Update the live consumers so they read the moved owner surface directly from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of the generic support module:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `tests/benchmarks/test_benchmark_manifest_validation.py`
- Tighten the ownership checks so this split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the helper-keyword contract names are defined on the source-tree owner module, not merely re-exported from `benchmark_test_support`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces the moved helper-keyword contract block
- Keep the cleanup structural only:
  - do not change benchmark manifest contents, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not add a new helper module, alias shim, or wrapper layer

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias or source_tree_support_module_exposes_routed_collection_owner_surface' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_|def _is_collection_replacement_compiled_pattern_keyword_error_workload\\()' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the source-tree compiled-pattern helper-keyword contract surface that still lives in the generic benchmark support module.
- Prefer moving the existing owner-specific data block onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over recreating it behind another wrapper or alias layer.

## Notes
- `RBR-1341` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1341|RBR-1342|RBR-1343|RBR-1344' ops/state/current_status.md ops/state/backlog.md || true` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_|def _is_collection_replacement_compiled_pattern_keyword_error_workload\\()' tests/benchmarks/benchmark_test_support.py` reports the remaining helper-keyword contract block in the generic support module
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` currently re-exports that block from `benchmark_test_support` instead of owning it
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already routes this slice through `source_tree_support`, while `tests/benchmarks/test_benchmark_manifest_validation.py` still reaches the same contract surface through `benchmark_test_support`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' -q` passed with `34 passed, 245 deselected in 0.19s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation' -q` passed with `3 passed, 61 deselected in 0.16s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias or source_tree_support_module_exposes_routed_collection_owner_surface' -q` passed with `5 passed, 85 deselected in 0.20s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_|def _is_collection_replacement_compiled_pattern_keyword_error_workload\\()' tests/benchmarks/benchmark_test_support.py"` currently fails because the source-tree-only helper-keyword contract block still lives in the generic support module, and that failure belongs exactly to this cleanup

## Completion
- Moved the compiled-pattern helper-keyword contract payload/spec/workload surface and the keyword-error classifier off `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, while keeping the shared contract dataclasses and helper-route primitives in the generic module.
- Updated `tests/benchmarks/test_benchmark_manifest_validation.py` to consume the owner-module helper-keyword contract surface directly from `source_tree_benchmark_anchor_support`.
- Tightened ownership checks so `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` now verifies the moved helper-keyword contract names are defined locally on the source-tree owner module rather than re-exported from `benchmark_test_support`, and `tests/benchmarks/test_benchmark_test_support.py` fails if the generic module reintroduces the moved block.

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias or source_tree_support_module_exposes_routed_collection_owner_surface' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_drops_source_tree_helper_keyword_contract_surface' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_|def _is_collection_replacement_compiled_pattern_keyword_error_workload\\()' tests/benchmarks/benchmark_test_support.py"`
