## RBR-1351: Centralize collection owner route inventories onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining test-local collection-owner route inventories from `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so the combined-suite route contract is described once on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of being mirrored in the consumer test module.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Add owner-owned inventory constants to `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` for the two collection-owned surfaces that the test module still mirrors locally:
  - `COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES`
  - `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES`
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to consume those owner-owned constants directly and delete these local mirror assignments:
  - `_MOVED_SOURCE_TREE_WORKLOAD_ID_NAMES`
  - `_COMBINED_SUITE_COLLECTION_SIGNATURE_HELPER_NAMES`
- Keep the cleanup bounded to this owner-inventory surface:
  - do not widen into `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not move the underlying workload-id constants or callable-signature helpers off `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - do not add a wrapper, alias shim, or new helper module
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or combined_suite_uses_collection_owner_conditional_callable_signature_helpers'`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_WORKLOAD_ID_NAMES|_COMBINED_SUITE_COLLECTION_SIGNATURE_HELPER_NAMES)\\b' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the inventory data onto the existing collection owner module over creating another shared helper surface.
- Keep the combined-suite boundary legible: the collection owner should publish its own route inventories, and the test should read those inventories instead of rebuilding the same tuples locally.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1351|RBR-1352|RBR-1353|RBR-1354' ops/state/current_status.md ops/state/backlog.md ops/tasks || true` returned only historical mentions inside completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- First candidate probe in this run found no remaining duplicate top-level helper definitions across the source-tree and collection owner modules, so this follow-on targets the next live owner-inventory mirror instead of reopening already-collapsed helper duplication.
- This owner-inventory mirror is live in the current checkout:
  - `rg -n '^(_MOVED_SOURCE_TREE_WORKLOAD_ID_NAMES|_COMBINED_SUITE_COLLECTION_SIGNATURE_HELPER_NAMES)\\b' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` reports the two remaining local mirror constants on the test module
  - `rg -n '^(COLLECTION_REPLACEMENT_ROUTED_SOURCE_TREE_WORKLOAD_ID_NAMES|COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_SIGNATURE_HELPER_NAMES)\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py` currently returns no matches because the owner module does not yet publish those inventories
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or combined_suite_uses_collection_owner_conditional_callable_signature_helpers'` passed with `2 passed, 146 deselected in 0.29s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_WORKLOAD_ID_NAMES|_COMBINED_SUITE_COLLECTION_SIGNATURE_HELPER_NAMES)\\b' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because those two mirrored constants still live on the test module, and that failure belongs exactly to this cleanup
- 2026-03-26T00:00:00+00:00: landed by adding the routed source-tree workload-id and conditional-callable helper inventories to `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and switching `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to consume those owner-owned tuples directly instead of mirroring them locally.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or combined_suite_uses_collection_owner_conditional_callable_signature_helpers'` -> `2 passed, 146 deselected in 0.38s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> passed
  - `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_WORKLOAD_ID_NAMES|_COMBINED_SUITE_COLLECTION_SIGNATURE_HELPER_NAMES)\\b' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` -> passed
