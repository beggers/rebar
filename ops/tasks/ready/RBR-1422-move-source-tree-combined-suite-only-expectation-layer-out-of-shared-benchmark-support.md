## RBR-1422: Move the source-tree-combined suite-only expectation layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the large `SourceTree*` expectation/case layer from `tests/benchmarks/benchmark_test_support.py` now that it exists to serve `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` rather than multiple benchmark suites.
- Leave `tests/benchmarks/benchmark_test_support.py` as the home for genuinely shared benchmark helpers, synthetic workload builders, contract builders, and cross-suite assertions, while `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owns its own source-tree-combined manifest expectations, case builders, scorecard contract helpers, and slice selectors.
- Keep `tests/benchmarks/test_benchmark_test_support.py` as the contract suite that verifies the surviving shared support surface and the combined suite's import/ownership boundaries, instead of preserving a suite-local data layer inside the shared support module.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete the source-tree-combined suite-only expectation layer from `tests/benchmarks/benchmark_test_support.py`, including:
  - `SourceTreeBenchmarkCommonCase`
  - `SourceTreeManifestExpectation`
  - `SourceTreeDeferredExpectation`
  - `SourceTreeCombinedCase`
  - `SourceTreeCombinedPatternGroupExpectation`
  - `SourceTreeCombinedManifestShapeExpectation`
  - `SourceTreeCombinedFullyMeasuredManifestExpectation`
  - `SourceTreeCombinedManifestExpectationDefinition`
  - `SourceTreeCombinedSliceExpectation`
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `source_tree_combined_manifest_representative_measured_workload_ids(...)`
  - `source_tree_combined_target_manifest_ids(...)`
  - `source_tree_combined_case(...)`
  - `select_source_tree_combined_slice_rows(...)`
  - `assert_source_tree_benchmark_contract(...)`
- Rebuild that ownership inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keeping the combined-suite behavior and report-contract assertions intact without routing those suite-local definitions through `tests/benchmarks/benchmark_test_support.py`.
- Keep the genuinely shared source-tree contract-builder surface in `tests/benchmarks/benchmark_test_support.py` where it is still reused across suites or support-contract checks, including `_source_tree_contract_manifest(...)`, `_source_tree_contract_workload(...)`, the pattern-boundary and compiled-pattern contract-definition families, and `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)` if the benchmark support-contract suite still needs it.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it stops asserting that `benchmark_test_support` exports the moved source-tree-combined expectation names, and instead verifies that:
  - the combined suite owns those names locally or through its own aliases
  - `benchmark_test_support` no longer exposes the moved suite-only layer
  - the surviving shared support surface still routes through package imports without local duplicates
- Keep the task bounded to deleting that suite-only shared-support layer; do not reopen benchmark workload manifests, `python/rebar_harness/benchmarks.py`, `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, or broader benchmark-support decomposition.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_benchmark_contract or routes_owner_names_through_module_alias'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'class SourceTreeBenchmarkCommonCase|class SourceTreeManifestExpectation|class SourceTreeDeferredExpectation|class SourceTreeCombinedCase|class SourceTreeCombinedPatternGroupExpectation|class SourceTreeCombinedManifestShapeExpectation|class SourceTreeCombinedFullyMeasuredManifestExpectation|class SourceTreeCombinedManifestExpectationDefinition|class SourceTreeCombinedSliceExpectation|^SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =|^def source_tree_combined_manifest_representative_measured_workload_ids|^def source_tree_combined_target_manifest_ids|^def source_tree_combined_case\\(|^def select_source_tree_combined_slice_rows\\(|^def assert_source_tree_benchmark_contract\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1422|RBR-1423|RBR-1424" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1422` was not reserved by planning-owned frontier notes.
- Candidate selection in this run:
  - First probe: `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` is still a viable standalone suite, but the remaining structure there reads as an independent publication-runtime test lane rather than a dead shared-support wrapper, so I did not queue a file-merge task on that basis alone.
  - Second probe: the `SourceTree*` expectation/case layer in `tests/benchmarks/benchmark_test_support.py` is referenced overwhelmingly by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, while the shared support file still carries dozens of source-tree-combined-only dataclasses, manifest registries, slice selectors, and scorecard helpers.
  - That makes this the bounded post-JSON architectural deletion with the clearest cross-file payoff: shrink the shared benchmark support surface by moving the combined-suite-only data/contract layer back into the combined suite and tightening the support-contract tests around the surviving shared layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined or source_tree_benchmark_contract or routes_owner_names_through_module_alias'` passed with `317 passed, 169 deselected, 1573 subtests passed in 13.12s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n 'class SourceTreeBenchmarkCommonCase|class SourceTreeManifestExpectation|class SourceTreeDeferredExpectation|class SourceTreeCombinedCase|class SourceTreeCombinedPatternGroupExpectation|class SourceTreeCombinedManifestShapeExpectation|class SourceTreeCombinedFullyMeasuredManifestExpectation|class SourceTreeCombinedManifestExpectationDefinition|class SourceTreeCombinedSliceExpectation|^SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =|^def source_tree_combined_manifest_representative_measured_workload_ids|^def source_tree_combined_target_manifest_ids|^def source_tree_combined_case\\(|^def select_source_tree_combined_slice_rows\\(|^def assert_source_tree_benchmark_contract\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact shared-support layer this task deletes.
