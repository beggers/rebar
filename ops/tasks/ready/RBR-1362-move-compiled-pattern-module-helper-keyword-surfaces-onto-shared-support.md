## RBR-1362: Move compiled-pattern module-helper keyword surfaces onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for compiled-pattern module-helper keyword contract surfaces so the contract specs, workload inventories, contract-surface params, and precompile anchor selection live on `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move these compiled-pattern module-helper keyword surfaces into `tests/benchmarks/benchmark_test_support.py`:
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
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume those shared names and delete the local definitions entirely rather than leaving a wrapper, alias shim, or duplicate owner inventory behind.
- Update the touched benchmark consumer suites to read those surfaces from `tests.benchmarks.benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Update the touched owner-surface tests so those names are treated as shared-support owned and no longer counted as source-tree-local or source-tree-routed inventory.
- Keep the cleanup bounded to compiled-pattern module-helper keyword contract-surface relocation:
  - do not move `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
  - do not move unrelated source-tree combined-slice helpers or scorecard expectations
  - do not change manifest selection semantics, contract payload semantics, or benchmark runtime behavior

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or test_compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_success_contract_workloads or test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_contract_workloads or test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS|_is_collection_replacement_compiled_pattern_keyword_error_workload)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS|_is_collection_replacement_compiled_pattern_keyword_error_workload)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting the source-tree transit layer over moving it sideways; these helper-keyword contract surfaces are already built from shared contract classes, shared manifest selectors, and shared result-check helpers on `tests/benchmarks/benchmark_test_support.py`.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-only benchmark definitions, combined-slice expectations, and owner surfaces that are still actually source-tree-specific after this cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1362|RBR-1363|RBR-1364' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still locally defines the compiled-pattern module-helper keyword contract specs, workload inventories, contract-surface params, and precompile-anchor workload selection even though those surfaces are built from shared manifest selectors and shared contract helper types on `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still consume those shared helper-keyword surfaces through `source_tree_support`
  - `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still encode those names as source-tree-owned rather than shared-support-owned, so one bounded cross-file cleanup is required to retire the transit layer cleanly
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or test_compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes'` passed with `4 passed, 60 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_success_contract_workloads or test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_contract_workloads or test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'` passed with `13 passed, 266 deselected in 0.12s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS|_is_collection_replacement_compiled_pattern_keyword_error_workload)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared benchmark support module does not yet define those helper-keyword surfaces, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS|_is_collection_replacement_compiled_pattern_keyword_error_workload)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those helper-keyword definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` currently fails because the touched benchmark suites still route those helper-keyword surfaces through `source_tree_support`, and that failure belongs exactly to this cleanup
