## RBR-1347: Delete source-tree collection-replacement workload-id aliases

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining collection-replacement workload-id passthrough block from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the combined source-tree benchmark suite stops routing those workload-id owners through a source-tree alias layer instead of importing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` directly.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove the collection-replacement workload-id passthrough assignments from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import `tests.benchmarks.collection_replacement_benchmark_anchor_support` directly and use that owner module for the workload-id surface above instead of `source_tree_support`.
- Update the ownership tests so the new boundary stays pinned:
  - `tests/benchmarks/test_benchmark_test_support.py` should stop asserting that the combined suite reaches this workload-id surface only through `source_tree_support`, and should instead fail if the combined suite reintroduces those workload-id aliases on `source_tree_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` should prove the combined suite routes the moved workload-id surface through the direct `collection_replacement_support` import without local rebinding
- Keep the cleanup bounded:
  - do not widen into moving or rerouting the remaining collection-replacement signature-helper passthroughs, compiled-pattern helper passthroughs, or `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_*` helper-name inventories in the same task
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add another alias shim or helper module

## Verification
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'template_round_trip or none_count or callable_alternation or template_bytes'`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_owner_surface_reaches_combined_suite or collection_replacement_support_reaches_source_tree_owner_surface'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the task limited to the collection-replacement workload-id alias block that currently duplicates owner data already defined in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Leave the remaining source-tree-owned collection-replacement signature-helper routing and compiled-pattern contract support for later follow-ons.

## Notes
- `RBR-1347` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1347|RBR-1348|RBR-1349|RBR-1350' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py` shows all ten passthrough assignments still live on the source-tree owner module even though the real owner definitions already exist in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `rg -n 'source_tree_support\\.(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the combined suite still consuming that workload-id owner surface through `source_tree_support`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'template_round_trip or none_count or callable_alternation or template_bytes'` passed with `5 passed, 274 deselected, 72 subtests passed in 0.85s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_owner_surface_reaches_combined_suite_through_source_tree_support_only or collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias'` passed with `2 passed, 138 deselected in 0.16s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because that workload-id alias block still lives on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the combined suite still routes those workload-id references through `source_tree_support`, and that failure belongs exactly to this cleanup

## Completion
- Removed the ten collection-replacement workload-id passthrough assignments from `tests/benchmarks/source_tree_benchmark_anchor_support.py` and trimmed the routed owner-name inventory to the surviving source-tree-owned workload-id surface.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import `collection_replacement_benchmark_anchor_support` directly and consume the moved workload-id tuples through `collection_replacement_support`.
- Retuned the ownership tests so the combined suite now proves direct `collection_replacement_support` routing for the moved workload-id surface and fails if those aliases reappear on `source_tree_support`.
- Verification in this implementation run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'template_round_trip or none_count or callable_alternation or template_bytes'`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_owner_surface_reaches_combined_suite or collection_replacement_support_reaches_source_tree_owner_surface'`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers'`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_routed_collection_owner_surface or collection-owner-routed-constants'`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
  - `bash -lc "! rg -n 'source_tree_support\\.(CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS|CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
