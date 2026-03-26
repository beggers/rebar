## RBR-1342: Move source-tree combined route helpers onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-combined-suite routing helper surface from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops owning source-tree-only AST/import-route helpers and `tests/benchmarks/source_tree_benchmark_anchor_support.py` becomes the only owner for that route-contract surface.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Move the source-tree-combined-suite routing helpers out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_source_tree_combined_suite_module`
  - `_parsed_source_tree_combined_suite_ast`
  - `_assert_source_tree_combined_routes_owner_names_through_module_alias`
- Leave genuinely shared AST/import primitives in `tests/benchmarks/benchmark_test_support.py`:
  - do not widen into moving `_module_alias_names`, `_parsed_module_ast`, `_module_import_targets`, `_ast_import_targets`, or `top_level_module_definition_and_assignment_names`
  - route the moved helpers through those existing shared primitives instead of adding a new wrapper or alias layer
- Update cache clearing so `tests/benchmarks/benchmark_test_support.py` no longer names the moved helpers locally while `anchor_support_cache_guard` still clears any cached source-tree owner helpers when that module is loaded.
- Update the live consumers so source-tree-owner tests read the moved helper surface from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of `benchmark_test_support`:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- Tighten the ownership checks so the split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the moved routing helpers are defined on the source-tree owner module, not merely re-exported from `benchmark_test_support`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces those moved source-tree route helpers
- Keep the cleanup structural only:
  - do not change benchmark manifest contents, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not add a new helper module, alias shim, or wrapper layer

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'combined_suite_routes_moved_support_surfaces_through_source_tree_support or combined_suite_imports_source_tree_support_through_owner_module_only or combined_suite_no_longer_imports_or_reads_collection_owner_surface_directly' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers or quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (_source_tree_combined_suite_module|_parsed_source_tree_combined_suite_ast|_assert_source_tree_combined_routes_owner_names_through_module_alias)\\(' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the source-tree-combined-suite route helper surface that still lives in the generic benchmark support module.
- Prefer moving that owner-specific helper surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over recreating it behind another generic helper or test-only shim.

## Notes
- `RBR-1342` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1341|RBR-1342|RBR-1343|RBR-1344|RBR-1345' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `tests/benchmarks/benchmark_test_support.py` still defines `_source_tree_combined_suite_module`, `_parsed_source_tree_combined_suite_ast`, and `_assert_source_tree_combined_routes_owner_names_through_module_alias`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still consume that route-helper surface through `benchmark_test_support`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` does not yet own those helpers
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'combined_suite_routes_moved_support_surfaces_through_source_tree_support or combined_suite_imports_source_tree_support_through_owner_module_only or combined_suite_no_longer_imports_or_reads_collection_owner_surface_directly' -q` passed with `12 passed, 78 deselected in 1.17s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers or quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers' -q` passed with `3 passed, 143 deselected in 0.37s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^def (_source_tree_combined_suite_module|_parsed_source_tree_combined_suite_ast|_assert_source_tree_combined_routes_owner_names_through_module_alias)\\(' tests/benchmarks/benchmark_test_support.py"` currently fails because the source-tree-only route helpers still live in the generic support module, and that failure belongs exactly to this cleanup

## Completion
- Moved `_source_tree_combined_suite_module`, `_parsed_source_tree_combined_suite_ast`, and `_assert_source_tree_combined_routes_owner_names_through_module_alias` off `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, keeping the route logic wired through the existing shared AST/import primitives in `benchmark_test_support`.
- Updated the generic cache guard so `tests/benchmarks/benchmark_test_support.py` no longer names those helpers locally while still clearing cached source-tree owner helpers through the loaded owner module.
- Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to consume the moved route-helper surface from `source_tree_benchmark_anchor_support`, and tightened `tests/benchmarks/test_benchmark_test_support.py` plus the source-tree owner tests so the split stays pinned.

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'combined_suite_routes_moved_support_surfaces_through_source_tree_support or combined_suite_imports_source_tree_support_through_owner_module_only or combined_suite_no_longer_imports_or_reads_collection_owner_surface_directly' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers or quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers' -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'no_longer_owns_source_tree_combined_routing_helpers or source_tree_combined_routing_helpers_stay_owner_scoped or source_tree_combined_route_helper_rejects_secondary_owner_alias_surface_refs or source_tree_combined_route_helper_rejects_direct_owner_surface_refs' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (_source_tree_combined_suite_module|_parsed_source_tree_combined_suite_ast|_assert_source_tree_combined_routes_owner_names_through_module_alias)\\(' tests/benchmarks/benchmark_test_support.py"`
