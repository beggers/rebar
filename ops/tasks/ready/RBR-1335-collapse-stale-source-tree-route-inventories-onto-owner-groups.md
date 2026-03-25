## RBR-1335: Collapse stale source-tree route inventories onto owner groups

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicated collection-owner route inventories that are still split across `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, so the post-`RBR-1334` source-tree combined-suite routing contract is owned from one source instead of being restated through stale local tuples and inline `owner_names=(...)` lists.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` with plain owner-owned route-contract groups for the collection-replacement-owned surface that the source-tree combined suite now reaches through `source_tree_support`. Keep this bounded to the currently duplicated post-`RBR-1334` route inventories:
  - the conditional-callable helper names now exported through `source_tree_support`
  - the routed collection-replacement workload-id tuple names now exported through `source_tree_support`
  - the routed collection-replacement signature/helper names now exported through `source_tree_support`
  - the one grouped route used by the collection-replacement suite to assert access to `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to consume those owner-owned route groups instead of keeping local `_MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES`, `_ROUTED_COLLECTION_REPLACEMENT_SOURCE_TREE_CONSTANT_NAMES`, and `_ROUTED_COLLECTION_REPLACEMENT_SOURCE_TREE_FUNCTION_NAMES` tuples in the test module.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to stop asserting against the removed `collection_replacement_support` alias in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; route its combined-suite owner-name assertions through `source_tree_support` using the same owner-owned route groups, and delete the inline `owner_names=(...)` lists from that file.
- Keep the cleanup structural only:
  - do not move the actual collection-replacement benchmark builders or workload/signature helpers out of `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - do not add a new support module, alias shim, or another route-through wrapper
  - do not widen into unrelated benchmark helper cleanup outside these routed-name inventories

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'owner_names=\\(' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`
- `bash -lc "! rg -n '^(_MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES|_ROUTED_COLLECTION_REPLACEMENT_SOURCE_TREE_(CONSTANT|FUNCTION)_NAMES) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Constraints
- Keep the task bounded to the stale route-contract inventories exposed by the post-`RBR-1334` source-tree owner flow.
- Prefer owner-owned tuples or similarly plain data on `tests/benchmarks/source_tree_benchmark_anchor_support.py` over introducing a new helper layer.

## Notes
- `RBR-1335` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1335|RBR-1336|RBR-1337|RBR-1338" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still contains three inline `owner_names=(...)` assertions, two of which now fail because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer imports `collection_replacement_support`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still carries the matching routed-name inventories as local tuple constants instead of one owner-owned source of truth
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the routed surface itself, so the remaining duplication is in test-side route-contract inventories rather than live benchmark behavior
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` currently fails on `test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers` and `test_conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers`, and those failures belong exactly to this stale-route cleanup
  - `bash -lc "! rg -n 'owner_names=\\(' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because that file still contains three inline owner-name lists
  - `bash -lc "! rg -n '^(_MOVED_CONDITIONAL_CALLABLE_HELPER_NAMES|_ROUTED_COLLECTION_REPLACEMENT_SOURCE_TREE_(CONSTANT|FUNCTION)_NAMES) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because those duplicated routed-name tuples still exist locally
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
