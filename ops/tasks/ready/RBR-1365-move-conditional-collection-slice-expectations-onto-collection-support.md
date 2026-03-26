## RBR-1365: Move conditional collection slice expectations onto collection support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for the conditional collection/replacement slice expectations so `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` owns its template/callable slice definitions directly instead of importing `tests/benchmarks/source_tree_benchmark_anchor_support.py` only to recover them.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move the `conditional-group-exists-boundary` collection-owned slice definitions below out of `tests/benchmarks/source_tree_benchmark_anchor_support.py` and define them on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead, preserving their existing slice ids, workload ids, row-category contracts, and representative-row semantics:
  - `minimal-template-replacement-rows`
  - `minimal-callable-replacement-rows`
  - `minimal-callable-replacement-exception-rows`
  - `minimal-callable-replacement-none-count-exception-rows`
  - `alternation-heavy-callable-replacement-rows`
  - `nested-callable-replacement-str-rows`
  - `nested-callable-replacement-bytes-rows`
  - `quantified-callable-replacement-str-rows`
  - `quantified-callable-replacement-bytes-rows`
- Remove the broker helper `def _conditional_group_exists_source_tree_slice_expectations()` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`; after this cleanup, that owner module should no longer import `source_tree_benchmark_anchor_support` just to recover its own slice expectation group.
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it composes `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` from the collection-owner slice expectation group instead of defining those nine collection-owned slice rows inline, and shrink `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_COMBINED_SLICE_OWNER_NAMES` so the source-tree owner no longer advertises the collection-owned slice-expectation surface as local.
- Update the touched benchmark-support tests and the combined suite so collection-owned slice-expectation checks route through `collection_replacement_support` rather than `source_tree_support`, while keeping the broader source-tree combined-manifest/slice machinery on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Preserve the current `conditional-group-exists-boundary` template/callable benchmark semantics, workload ordering, and scorecard alignment; this is a structural ownership cleanup, not a workload or report change.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or combined_suite_uses_collection_owner_conditional_callable_signature_helpers or quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'routes_collection_replacement_owner_names_through_alias or routed_collection_replacement_combined_slice_owner_names_stay_shared or source_tree_support_module_exposes_routed_collection_owner_surface'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `rg -n 'slice_id=\"(minimal-template-replacement-rows|minimal-callable-replacement-rows|minimal-callable-replacement-exception-rows|minimal-callable-replacement-none-count-exception-rows|alternation-heavy-callable-replacement-rows|nested-callable-replacement-str-rows|nested-callable-replacement-bytes-rows|quantified-callable-replacement-str-rows|quantified-callable-replacement-bytes-rows)\"' tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `bash -lc \"! rg -n 'slice_id=\\\"(minimal-template-replacement-rows|minimal-callable-replacement-rows|minimal-callable-replacement-exception-rows|minimal-callable-replacement-none-count-exception-rows|alternation-heavy-callable-replacement-rows|nested-callable-replacement-str-rows|nested-callable-replacement-bytes-rows|quantified-callable-replacement-str-rows|quantified-callable-replacement-bytes-rows)\\\"|def _conditional_group_exists_source_tree_slice_expectations\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py\"`

## Constraints
- Prefer deleting the transit layer over adding a new broker or compatibility alias back on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Keep the cleanup bounded to the conditional collection/replacement slice-expectation ownership boundary; do not widen into unrelated `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` rows, workload manifests, or benchmark publication behavior.
- Keep the broader source-tree combined-manifest expectation machinery on `tests/benchmarks/source_tree_benchmark_anchor_support.py`; this task is only for the collection-owned conditional template/callable slice group.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1365|RBR-1366|RBR-1367' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` still defines `def _conditional_group_exists_source_tree_slice_expectations()` at line `1824`, and that helper exists only to import `source_tree_benchmark_anchor_support` and recover collection-owned slice expectations.
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines the nine collection-owned `conditional-group-exists-boundary` template/callable slice rows inline at lines `3491`, `3544`, `3599`, `3642`, `3700`, `3761`, `3816`, `3875`, and `3909`.
  - The collection owner already owns the adjacent workload-id inventories and callable/template expectation helpers for this same surface, so moving the slice definition group there tightens ownership without widening into the rest of the source-tree combined benchmark support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import or combined_suite_uses_collection_owner_conditional_callable_signature_helpers or quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers'` passed with `4 passed, 144 deselected in 0.46s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'routes_collection_replacement_owner_names_through_alias or routed_collection_replacement_combined_slice_owner_names_stay_shared or source_tree_support_module_exposes_routed_collection_owner_surface'` passed with `1 passed, 104 deselected in 0.13s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice'` passed with `3 passed, 276 deselected in 0.14s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `rg -n 'slice_id=\"(minimal-template-replacement-rows|minimal-callable-replacement-rows|minimal-callable-replacement-exception-rows|minimal-callable-replacement-none-count-exception-rows|alternation-heavy-callable-replacement-rows|nested-callable-replacement-str-rows|nested-callable-replacement-bytes-rows|quantified-callable-replacement-str-rows|quantified-callable-replacement-bytes-rows)\"' tests/benchmarks/collection_replacement_benchmark_anchor_support.py` currently fails because that owner module does not yet define the slice group, and that failure belongs exactly to this cleanup
  - `bash -lc \"! rg -n 'slice_id=\\\"(minimal-template-replacement-rows|minimal-callable-replacement-rows|minimal-callable-replacement-exception-rows|minimal-callable-replacement-none-count-exception-rows|alternation-heavy-callable-replacement-rows|nested-callable-replacement-str-rows|nested-callable-replacement-bytes-rows|quantified-callable-replacement-str-rows|quantified-callable-replacement-bytes-rows)\\\"|def _conditional_group_exists_source_tree_slice_expectations\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py\"` currently fails because the broker helper still exists on the collection owner and the nine slice definitions still live on the source-tree owner, and that failure belongs exactly to this cleanup
