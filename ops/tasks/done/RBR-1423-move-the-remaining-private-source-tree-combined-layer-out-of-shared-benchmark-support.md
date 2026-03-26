## RBR-1423: Move the remaining private source-tree-combined layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining private source-tree-combined expectation/contract layer from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still aliases a large suite-local `_SourceTree*` surface and its manifest/slice helpers from shared support even though that layer now exists to serve the combined benchmark suite rather than multiple support modules.
- Leave `tests/benchmarks/benchmark_test_support.py` as the home for genuinely shared manifest-loading helpers, synthetic manifest builders, CPython workload runners, anchor contracts, and neutral benchmark assertions, while the combined suite owns its own private dataclasses, manifest-expectation registry, slice inventory, fallback/default expectation state, and source-tree-combined contract helper.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete the remaining private combined-suite layer from `tests/benchmarks/benchmark_test_support.py`, including:
  - `_SourceTreeBenchmarkCommonCase`
  - `_SourceTreeManifestExpectation`
  - `_SourceTreeDeferredExpectation`
  - `_SourceTreeCombinedCase`
  - `_SourceTreeCombinedPatternGroupExpectation`
  - `_SourceTreeCombinedManifestShapeExpectation`
  - `_SourceTreeCombinedFullyMeasuredManifestExpectation`
  - `_SourceTreeCombinedManifestExpectationDefinition`
  - `_SourceTreeCombinedManifestExpectations`
  - `_SourceTreeCombinedSliceExpectation`
  - `_combined_manifest_definition(...)`
  - `_combined_fully_measured_manifest_expectation(...)`
  - `_published_benchmark_manifest_ids()`
  - `_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION`
  - `_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - `_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS`
  - `_filter_manifest_workload_ids(...)`
  - `_public_source_tree_manifest_expectation(...)`
  - `_source_tree_combined_manifest_representative_measured_workload_ids(...)`
  - `_source_tree_combined_target_manifest_ids(...)`
  - `_expected_summary_for_manifests(...)`
  - `_source_tree_combined_case(...)`
  - `_workload_matches_source_tree_combined_slice(...)`
  - `_select_source_tree_combined_slice_rows(...)`
  - `_assert_source_tree_benchmark_contract(...)`
- Rebuild that layer inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined suite owns:
  - its private `_SourceTree*` dataclasses and registries
  - its default/fallback manifest-expectation handling
  - its slice selectors and scorecard helpers
  - its source-tree-combined contract assertion
- Tighten the combined suite boundary so it no longer aliases the moved private layer from `benchmark_test_support`, and remove `_SourceTreeSupportProxy` if the suite no longer needs that indirection after the move.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the support-contract suite stops treating that private combined-suite layer as `benchmark_test_support`-owned and instead verifies that:
  - `benchmark_test_support` no longer exposes the moved private names
  - the combined suite owns the moved private names locally
  - the surviving shared support surface still routes through package imports without reintroducing local duplicates
- Keep the task bounded to this one suite-local ownership move; do not reopen benchmark workload manifests, `python/rebar_harness/benchmarks.py`, reporting/state files, or broader helper-by-helper cleanup elsewhere in `tests/benchmarks/`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_benchmark_contract or routes_owner_names_through_module_alias'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'class _SourceTreeBenchmarkCommonCase|class _SourceTreeManifestExpectation|class _SourceTreeDeferredExpectation|class _SourceTreeCombinedCase|class _SourceTreeCombinedPatternGroupExpectation|class _SourceTreeCombinedManifestShapeExpectation|class _SourceTreeCombinedFullyMeasuredManifestExpectation|class _SourceTreeCombinedManifestExpectationDefinition|class _SourceTreeCombinedManifestExpectations|class _SourceTreeCombinedSliceExpectation|^def _combined_manifest_definition\\(|^def _combined_fully_measured_manifest_expectation\\(|^def _published_benchmark_manifest_ids\\(|^_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION =|^_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =|^SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS =|^_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS =|^def _filter_manifest_workload_ids\\(|^def _public_source_tree_manifest_expectation\\(|^def _source_tree_combined_manifest_representative_measured_workload_ids\\(|^def _source_tree_combined_target_manifest_ids\\(|^def _expected_summary_for_manifests\\(|^def _source_tree_combined_case\\(|^def _workload_matches_source_tree_combined_slice\\(|^def _select_source_tree_combined_slice_rows\\(|^def _assert_source_tree_benchmark_contract\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1423|RBR-1424|RBR-1425" ops/state/current_status.md ops/state/backlog.md ops/tasks` returned no planning-owned reservation for `RBR-1423`; only historical done-task notes mentioned later ids.
- Candidate selection in this run:
  - First probe: `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still aliases the entire private `_SourceTree*` expectation/contract surface from `tests/benchmarks/benchmark_test_support.py`, and most of those names appear exactly once at the top of the combined suite rather than serving multiple consumers.
  - `tests/benchmarks/benchmark_test_support.py` still carries the private dataclasses, fallback manifest-expectation registry, slice inventory, helper selectors, and contract assertion for that combined-suite lane, even after `RBR-1422` moved only the public ownership layer.
  - That makes this a bounded post-JSON architectural move with clear cross-file payoff: delete one remaining suite-local layer from shared benchmark support instead of widening into unrelated local helper cleanup.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_benchmark_contract or routes_owner_names_through_module_alias'` passed with `318 passed, 170 deselected, 1573 subtests passed in 13.35s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n 'class _SourceTreeBenchmarkCommonCase|class _SourceTreeManifestExpectation|class _SourceTreeDeferredExpectation|class _SourceTreeCombinedCase|class _SourceTreeCombinedPatternGroupExpectation|class _SourceTreeCombinedManifestShapeExpectation|class _SourceTreeCombinedFullyMeasuredManifestExpectation|class _SourceTreeCombinedManifestExpectationDefinition|class _SourceTreeCombinedManifestExpectations|class _SourceTreeCombinedSliceExpectation|^def _combined_manifest_definition\\(|^def _combined_fully_measured_manifest_expectation\\(|^def _published_benchmark_manifest_ids\\(|^_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION =|^_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =|^SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS =|^_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS =|^def _filter_manifest_workload_ids\\(|^def _public_source_tree_manifest_expectation\\(|^def _source_tree_combined_manifest_representative_measured_workload_ids\\(|^def _source_tree_combined_target_manifest_ids\\(|^def _expected_summary_for_manifests\\(|^def _source_tree_combined_case\\(|^def _workload_matches_source_tree_combined_slice\\(|^def _select_source_tree_combined_slice_rows\\(|^def _assert_source_tree_benchmark_contract\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact suite-local shared-support layer this task deletes.

## Completion
- Moved the remaining private source-tree-combined dataclasses, manifest-expectation registry, slice inventory, summary helpers, target-case builders, and source-tree benchmark contract assertion from `tests/benchmarks/benchmark_test_support.py` into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Left `tests/benchmarks/benchmark_test_support.py` with the shared manifest loaders, anchor-contract helpers, cache clearing, and route-enforcement utilities only; the acceptance grep now reports none of the moved private combined-suite names in that module.
- Updated `tests/benchmarks/test_benchmark_test_support.py` so it now verifies the private combined-suite names live on the combined suite, stay absent from shared support, and keep the surviving shared-support imports routed through the package import path.
- Kept `_SourceTreeSupportProxy` in the combined suite because the suite still consumes a large shared-support surface; the proxy now only provides shared-helper fallback plus access to the suite-owned local names, instead of hiding ownership of the moved private layer behind `benchmark_test_support`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_benchmark_contract or routes_owner_names_through_module_alias'`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `bash -lc "! rg -n 'class _SourceTreeBenchmarkCommonCase|class _SourceTreeManifestExpectation|class _SourceTreeDeferredExpectation|class _SourceTreeCombinedCase|class _SourceTreeCombinedPatternGroupExpectation|class _SourceTreeCombinedManifestShapeExpectation|class _SourceTreeCombinedFullyMeasuredManifestExpectation|class _SourceTreeCombinedManifestExpectationDefinition|class _SourceTreeCombinedManifestExpectations|class _SourceTreeCombinedSliceExpectation|^def _combined_manifest_definition\\(|^def _combined_fully_measured_manifest_expectation\\(|^def _published_benchmark_manifest_ids\\(|^_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION =|^_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =|^SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS =|^_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS =|^def _filter_manifest_workload_ids\\(|^def _public_source_tree_manifest_expectation\\(|^def _source_tree_combined_manifest_representative_measured_workload_ids\\(|^def _source_tree_combined_target_manifest_ids\\(|^def _expected_summary_for_manifests\\(|^def _source_tree_combined_case\\(|^def _workload_matches_source_tree_combined_slice\\(|^def _select_source_tree_combined_slice_rows\\(|^def _assert_source_tree_benchmark_contract\\(' tests/benchmarks/benchmark_test_support.py"`
