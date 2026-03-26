## RBR-1375: Delete collection-replacement routed-name inventories

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the bookkeeping-only routed-name inventories from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and rewrite the affected ownership assertions in the collection/source-tree benchmark-support tests to use direct targeted checks instead of owner-exported name lists.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these exported bookkeeping inventories from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without moving them sideways or replacing them with another exported registry:
  - `COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES`
  - `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES`
  - `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES`
- Rewrite the affected assertions in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so they preserve the same owner boundaries through direct targeted checks rather than through those exported tuple inventories. Preserve these boundaries explicitly:
  - the source-tree combined suite still reads the routed conditional workload-id constants through the `collection_replacement_support` module alias instead of direct owner imports or local reassignments;
  - the conditional callable helper functions and callable-signature helpers remain defined on `tests.benchmarks.collection_replacement_benchmark_anchor_support`, not on `tests.benchmarks.source_tree_benchmark_anchor_support` and not as local functions in the combined suite;
  - the combined-suite route assertions still prove the collection-replacement owner is accessed through the package alias path rather than through direct imports or duplicated local owner-name inventories.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_ROUTED_(SOURCE_TREE_WORKLOAD_ID_NAMES|CONDITIONAL_CALLABLE_HELPER_NAMES|CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the routed-name inventories over recreating them under new names, moving them into another owner module, or replacing them with another mirrored test-only list.
- Keep the run bounded to this single collection/source-tree benchmark-support ownership cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1375|RBR-1376|RBR-1377' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Post-JSON cleanup stayed in the benchmark-support ownership layer because tracked and live JSON counts are both zero.
  - `COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES`, `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES`, and `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES` are defined only in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
  - Those three inventories have no live references inside `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`; they only feed ownership assertions in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`.
  - The current green benchmark-support suites already pass without any runtime consumer depending on those tuple exports, which makes them a bounded bookkeeping-only cleanup target rather than live harness behavior.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `424 passed in 3.11s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"` currently fails because those exported bookkeeping inventories still exist, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_ROUTED_(SOURCE_TREE_WORKLOAD_ID_NAMES|CONDITIONAL_CALLABLE_HELPER_NAMES|CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the affected ownership tests still read those bookkeeping inventories from the owner module, and that failure belongs exactly to this cleanup

## Completion
- Deleted `COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES`, `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES`, and `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Rewrote the affected collection/source-tree ownership assertions to name the routed workload-id constants and callable helper surfaces directly instead of consuming exported tuple inventories.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` -> `424 passed in 3.30s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `bash -lc "! rg -n '^(COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"`
  - `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_ROUTED_(SOURCE_TREE_WORKLOAD_ID_NAMES|CONDITIONAL_CALLABLE_HELPER_NAMES|CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`
