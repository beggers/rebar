## RBR-1354: Centralize retired benchmark owner inventories onto owner modules

Status: done
Owner: architecture-implementation
Created: 2026-03-26
Completed: 2026-03-26

## Goal
- Delete the remaining retired-owner inventory mirrors from `tests/benchmarks/test_benchmark_test_support.py` so source-tree, manifest-validation, and collection owner surfaces are described once on their owning support modules instead of being duplicated in a consumer test file.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Add owner-owned retired-name inventory constants for the consumer-route checks that `tests/benchmarks/test_benchmark_test_support.py` still mirrors locally:
  - one source-tree combined-suite retired-owner inventory on `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - one manifest-validation retired-owner inventory on `tests/benchmarks/benchmark_test_support.py`
  - one collection-owner retired benchmark-surface inventory on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- Update `tests/benchmarks/test_benchmark_test_support.py` to consume those owner-owned constants directly and delete these local mirror assignments:
  - `_SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES`
  - `_BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES`
  - `_COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES`
- Keep the cleanup bounded to this inventory-centralization surface:
  - do not move the underlying helper implementations or workload-id constants off their current owner modules
  - do not widen into source-tree combined helper extraction, manifest logic, benchmark manifests, or harness behavior
  - do not add a new helper module, wrapper shim, or alias layer
  - do not change scorecards, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_manifest_validation_routes_owner_surface_through_benchmark_test_support or collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias or do_not_alias_owner_module_surfaces'`
- `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES|_BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES|_COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES)\\b' tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer moving the inventory data onto the existing owner modules over adding another shared assertion helper.
- Keep the consumer-route contract legible: owner modules should publish the retired names they own, and `tests/benchmarks/test_benchmark_test_support.py` should read those inventories instead of rebuilding them.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1354|RBR-1355|retired owner|retired_owner|retired benchmark owner|retired shared support' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only historical mentions inside completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `rg -n '^(_SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES|_BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES|_COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES)\\b' tests/benchmarks/test_benchmark_test_support.py` reports three remaining test-local retired-owner inventory constants
  - those inventories describe owner-module surfaces, but the owner modules do not yet publish equivalent route inventories for the consumer test to reuse
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_manifest_validation_routes_owner_surface_through_benchmark_test_support or collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias or do_not_alias_owner_module_surfaces'` passed with `5 passed, 147 deselected in 0.18s`
  - `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(_SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES|_BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES|_COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES)\\b' tests/benchmarks/test_benchmark_test_support.py"` currently fails because those three mirrored constants still live on the consumer test module, and that failure belongs exactly to this cleanup
- Completion note:
  - Added owner-owned retired-name inventories to `tests/benchmarks/source_tree_benchmark_anchor_support.py`, `tests/benchmarks/benchmark_test_support.py`, and `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, then rewired `tests/benchmarks/test_benchmark_test_support.py` to consume those exported constants directly.
  - Verification in this run:
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'consumer_suites_reuse_shared_support_without_local_duplicates or benchmark_manifest_validation_routes_owner_surface_through_benchmark_test_support or collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias or do_not_alias_owner_module_surfaces'` passed with `5 passed, 147 deselected in 0.33s`
    - `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` passed
    - `bash -lc "! rg -n '^(_SOURCE_TREE_COMBINED_RETIRED_OWNER_NAMES|_BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES|_COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES)\\b' tests/benchmarks/test_benchmark_test_support.py"` passed
