## RBR-1366: Delete source-tree collection selector alias

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the last collection-replacement workload-selector transit alias from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the shared compiled-pattern success selector is owned only by `tests/benchmarks/benchmark_test_support.py`, while the collection-replacement owner continues to consume it directly from shared support.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Remove `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_WORKLOAD_ID_NAMES` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Remove the `_is_collection_replacement_compiled_pattern_success_workload` assignment alias from `tests/benchmarks/source_tree_benchmark_anchor_support.py`; after this cleanup, that module should no longer advertise the shared collection-replacement compiled-pattern success selector as local surface.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the routed-surface checks stop expecting a collection-owner workload-id alias on `source_tree_support`, while preserving the existing routed-surface assertions for the still-legitimate moved support names.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the ownership check verifies `_is_collection_replacement_compiled_pattern_success_workload` stays on `tests/benchmarks/benchmark_test_support.py` directly rather than through `source_tree_benchmark_anchor_support.py`.
- Keep `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` verifying that `collection_replacement_benchmark_anchor_support.py` consumes the shared selector directly from `benchmark_test_support` and does not gain a new local alias.
- Preserve the current collection-replacement compiled-pattern benchmark semantics, owner specs, workload filtering, and combined-suite behavior; this is a transit-layer deletion, not a workload or report change.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_routed_collection_owner_surface or combined_suite_routes_moved_support_surfaces_through_source_tree_support'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'compiled_pattern_success_selector_routes_through_shared_support_without_local_definition or compiled_pattern_success_workloads_stay_in_scope_and_keep_expected_signature'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_compiled_pattern_success_selector_stays_owned_by_shared_support'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'source_tree_support\\._is_collection_replacement_compiled_pattern_success_workload' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `bash -lc "! rg -n '^SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_WORKLOAD_ID_NAMES|^_is_collection_replacement_compiled_pattern_success_workload =' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the transit alias over introducing a new compatibility alias on another owner module.
- Keep the cleanup bounded to the collection-replacement compiled-pattern success selector ownership boundary; do not widen into unrelated source-tree combined-slice machinery or other shared-support helpers in the same run.
- Do not change benchmark workload definitions, benchmark publication code, or correctness/benchmark semantics.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1366|RBR-1367|RBR-1368' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still declares `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_WORKLOAD_ID_NAMES` at line `2268` even though it now contains only `_is_collection_replacement_compiled_pattern_success_workload`.
  - The same file still assigns `_is_collection_replacement_compiled_pattern_success_workload = benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload` at line `4405`.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` does not reference `source_tree_support._is_collection_replacement_compiled_pattern_success_workload`; the combined suite already uses `benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload` directly.
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` already consumes the shared selector directly from `benchmark_test_support`, so the source-tree alias is only transit bookkeeping.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_routed_collection_owner_surface or combined_suite_routes_moved_support_surfaces_through_source_tree_support'` passed with `8 passed, 98 deselected in 0.76s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'compiled_pattern_success_selector_routes_through_shared_support_without_local_definition or compiled_pattern_success_workloads_stay_in_scope_and_keep_expected_signature'` passed with `2 passed, 146 deselected in 0.12s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_compiled_pattern_success_selector_stays_owned_by_shared_support'` passed with `1 passed, 169 deselected in 0.29s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `bash -lc "! rg -n 'source_tree_support\\._is_collection_replacement_compiled_pattern_success_workload' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed
  - `bash -lc "! rg -n '^SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_WORKLOAD_ID_NAMES|^_is_collection_replacement_compiled_pattern_success_workload =' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because both the routed-name tuple and the alias assignment still exist, and that failure belongs exactly to this cleanup
