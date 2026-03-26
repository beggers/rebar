## RBR-1412: Move the compiled-pattern helper keyword contract surface onto collection owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining collection-replacement-owned contract layer from `tests/benchmarks/benchmark_test_support.py`.
- The compiled-pattern module-helper keyword contract dataclasses, `_CompiledPatternModuleHelperKeywordContractSpec` and `_CompiledPatternModuleHelperKeywordContractSurface`, still live in shared benchmark support even though the only active owner for that lane is `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Move that contract type/surface pair onto collection-replacement owner support so shared benchmark support keeps only generic helpers and shared payload-drop constants.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete `_CompiledPatternModuleHelperKeywordContractSpec` and `_CompiledPatternModuleHelperKeywordContractSurface` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate `_CompiledPatternModuleHelperKeywordContractSpec` and `_CompiledPatternModuleHelperKeywordContractSurface` on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` with the same method names, behavior, and dataclass shape:
  - `_CompiledPatternModuleHelperKeywordContractSpec.expected_materialized_field_names(...)`
  - `_CompiledPatternModuleHelperKeywordContractSpec.contract_builder_spec(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.source_workloads(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.precompile_source_workloads(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.expected_build_calls(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.expected_callback_call(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.expected_callback_result(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.run_cpython_helper_workload(...)`
  - `_CompiledPatternModuleHelperKeywordContractSurface.assert_outcome(...)`
- Update `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so its `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_*` spec/surface constants instantiate the local classes instead of `benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec` and `benchmark_test_support._CompiledPatternModuleHelperKeywordContractSurface`.
- Update `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so ownership/type assertions treat the compiled-pattern helper keyword contract lane as collection-replacement-owned instead of shared-support-owned.
- Remove direct `benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec` and `benchmark_test_support._CompiledPatternModuleHelperKeywordContractSurface` references from:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_benchmark_test_support.py`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - any other scoped benchmark-owner test touched by this lane
- Keep genuinely shared benchmark helpers and constants in `tests/benchmarks/benchmark_test_support.py`, including:
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS`
  - `COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS`
  - `compiled_pattern_contract_expected_build_calls(...)`
  - `assert_benchmark_workload_matches_expected_result(...)`
  - `run_benchmark_workload_with_cpython(...)`
- Do not widen into the source-tree contract-builder lane, compiled-pattern compile owner lane, wrong-text-model owner lane, benchmark manifests, reports, or tracked project-state docs.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder_owner_methods_return_live_specs or collection_replacement_support_exports_compiled_pattern_module_helper_keyword_contract_surface or compiled_pattern_module_helper_keyword_surface_moves_to_collection_replacement_owner'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates' tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field' tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'class _CompiledPatternModuleHelperKeywordContractSpec|class _CompiledPatternModuleHelperKeywordContractSurface' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "! rg -n 'benchmark_test_support\\._CompiledPatternModuleHelperKeywordContract(Spec|Surface)' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1412|RBR-1413|RBR-1414' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks` found no reserved future-id use for `RBR-1412`; the only hit was the historical note inside `ops/tasks/done/RBR-1411-move-source-tree-contract-builder-spec-onto-source-tree-owner-support.md`.
- Candidate selection in this run:
  - `rg -n "_CompiledPatternModuleHelperKeywordContractSpec|_CompiledPatternModuleHelperKeywordContractSurface" ...` shows the class definitions still live in `tests/benchmarks/benchmark_test_support.py`, while the live owner constants and consumers sit in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` plus scoped benchmark-owner tests.
  - That makes this the next bounded post-JSON simplification: it removes one complete collection-owned contract type/surface layer from shared benchmark support without inventing a new owner module or widening into unrelated benchmark lanes.
  - I stopped after this first viable candidate because it removes an entire remaining shared-to-owner routing layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder_owner_methods_return_live_specs or collection_replacement_support_exports_compiled_pattern_module_helper_keyword_contract_surface or compiled_pattern_module_helper_keyword_surface_moves_to_collection_replacement_owner'` passed with `13 passed, 167 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates' tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field' tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'` passed with `55 passed, 566 deselected in 0.22s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'class _CompiledPatternModuleHelperKeywordContractSpec|class _CompiledPatternModuleHelperKeywordContractSurface' tests/benchmarks/benchmark_test_support.py"` currently fails only because those exact shared-support class definitions are still present.
  - `bash -lc "! rg -n 'benchmark_test_support\\._CompiledPatternModuleHelperKeywordContract(Spec|Surface)' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails only because the owner module and scoped tests still route through `benchmark_test_support`, which is the exact cleanup this task queues.
  - I intentionally excluded `tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder_surface_uses_one_owned_route'` from acceptance because it is already red in the current checkout for an unrelated owner-module AST assertion (`CompiledPatternModuleCompileContractCase` lookup) before this cleanup lands.
