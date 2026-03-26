## RBR-1361: Move compiled-pattern module-compile owner specs onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for shared compiled-pattern module-compile contract surfaces so the owner-spec constants, contract cases, anchor lanes, and source-workload params live on `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Move these shared module-compile surfaces into `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume the shared compile surfaces and delete the local definitions entirely rather than leaving a wrapper, alias shim, or duplicate owner inventory behind.
- Update the touched consumer suites to read those five names from `tests.benchmarks.benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Update the touched owner-surface tests so those five names are treated as shared-support owned and no longer counted as source-tree-local or source-tree-routed inventory.
- Keep the cleanup bounded to module-compile contract-surface relocation:
  - do not move `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_*` surfaces in the same task
  - do not move the compiled-pattern wrong-text-model surfaces in the same task
  - do not change workload selectors, contract payload semantics, or runtime benchmark behavior

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or test_standard_benchmark_compiled_pattern_module_compile_contract_rejects_bool_keyword_type_mismatch'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_compile_owner_specs_keep_module_boundary_rows_measured or test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or test_compiled_pattern_module_compile_contract_callbacks_precompile_first_argument_before_timing'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the source-tree transit layer over moving it sideways; these compile contract surfaces are already built from shared selectors, shared contract helpers, and shared contract-owner types on `tests/benchmarks/benchmark_test_support.py`.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-combined expectations, source-tree-only workload inventories, and helper surfaces that are still actually owner-specific after this cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1361|RBR-1362|RBR-1363' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still locally defines `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`, `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`, `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`, `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`, and `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` even though those surfaces are built from shared selectors, shared contract helpers, and shared owner types on `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still consume those shared compile surfaces through `source_tree_support`
  - `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still encode that those five names are source-tree owned rather than shared-support owned
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or test_standard_benchmark_compiled_pattern_module_compile_contract_rejects_bool_keyword_type_mismatch'` passed with `7 passed, 57 deselected in 0.13s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_compile_owner_specs_keep_module_boundary_rows_measured or test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or test_compiled_pattern_module_compile_contract_callbacks_precompile_first_argument_before_timing'` passed with `10 passed, 94 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared benchmark support module does not yet define those five compile surfaces, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those five definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the benchmark consumer suites still route those shared compile surfaces through `source_tree_support`, and that failure belongs exactly to this cleanup
