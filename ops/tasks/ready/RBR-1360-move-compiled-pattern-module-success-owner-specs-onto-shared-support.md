## RBR-1360: Move compiled-pattern module-success owner specs onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for shared compiled-pattern module-success contract specs so the owner-spec constants and source-workload params live on `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Move these shared module-success surfaces into `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume the shared owner specs and params, and delete the local definitions entirely rather than leaving a wrapper, alias shim, or duplicate inventory constant behind.
- Update the touched consumer suites to read those four names from `tests.benchmarks.benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Update the touched owner-surface tests so those four names are treated as shared-support owned and no longer counted as source-tree-local or source-tree-routed inventory.
- Keep the cleanup bounded to module-success contract-surface relocation:
  - do not move `live_compiled_pattern_module_success_surface_ids`
  - do not move the compiled-pattern module-compile contract cases in the same task
  - do not move the helper-keyword contract specs in the same task
  - do not change workload selectors, contract payload semantics, or runtime benchmark behavior

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_helper_owner_specs_keep_zero_gap_rows_measured or test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads or test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the source-tree transit layer over moving it sideways; these owner specs already depend on selectors and contract helpers that live on `tests/benchmarks/benchmark_test_support.py`.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-combined expectations, source-tree-only workload inventories, and helper surfaces that are still actually owner-specific after this cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1360|RBR-1361|RBR-1362' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still locally defines `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`, and `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` even though those specs are built from shared selectors and shared contract helpers in `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still consume those shared module-success surfaces through `source_tree_support`
  - `tests/benchmarks/test_benchmark_test_support.py` still hard-codes that those four names must not exist on `tests/benchmarks/benchmark_test_support.py`, so the current checkout still carries a real source-tree transit layer instead of a shared-support home
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_helper_owner_specs_keep_zero_gap_rows_measured or test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads or test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'` passed with `43 passed, 236 deselected in 0.81s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared benchmark support module does not yet define those four module-success surfaces, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those four definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\\b' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the benchmark consumer suites still route those shared module-success surfaces through `source_tree_support`, and that failure belongs exactly to this cleanup
