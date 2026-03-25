# RBR-1294: Move source-tree combined case support onto source-tree anchor support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining reusable source-tree case-model and case-selection layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` owner, so the giant combined benchmark suite stops carrying both the assertions and the support API that feeds them.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it owns the reusable source-tree combined-case model that currently lives inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including these dataclasses:
  - `SourceTreeBenchmarkCommonCase`
  - `SourceTreeManifestExpectation`
  - `SourceTreeDeferredExpectation`
  - `SourceTreeScorecardCase`
  - `SourceTreeCombinedCase`
  - `SourceTreeCombinedPatternGroupExpectation`
  - `SourceTreeCombinedManifestShapeExpectation`
  - `SourceTreeCombinedFullyMeasuredManifestExpectation`
  - `SourceTreeCombinedManifestExpectationDefinition`
  - `SourceTreeCombinedSliceExpectation`
- Move the supporting source-tree case-definition/query surface that those types depend on onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` as well, keeping the current behavior intact:
  - `SOURCE_TREE_SCORECARD_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - `source_tree_scorecard_case_ids`
  - `source_tree_scorecard_case`
  - `source_tree_combined_target_manifest_ids`
  - `source_tree_combined_case`
  - `source_tree_combined_manifest_shape_expectation`
  - `source_tree_combined_slice_manifest_ids`
  - `source_tree_combined_slice_derived_manifest_ids`
  - `source_tree_combined_slice_expectations`
  - `source_tree_combined_fully_measured_manifest_ids`
  - `source_tree_combined_fully_measured_manifest_expectation`
  - `source_tree_combined_manifest_representative_measured_workload_ids`
  - `expected_summary_for_manifests`
  - `representative_measured_workload_ids`
  - `select_source_tree_combined_slice_rows`
  - any small helper functions that are only there to build or query that moved support surface
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved source-tree case-support API from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of defining that support inline. After the cleanup, the combined suite should keep only benchmark assertions and test-local helpers that are still specific to the suite itself.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it pins the slimmer ownership boundary directly:
  - assert the moved source-tree case-support API is exposed from `tests.benchmarks.source_tree_benchmark_anchor_support`;
  - assert `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines the moved dataclasses or top-level case-builder/query helpers locally; and
  - keep the existing source-tree anchor-support assertions green.
- Do not add a new helper broker module for this task. Reuse `tests/benchmarks/source_tree_benchmark_anchor_support.py` as the owner for the moved source-tree case-support layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(class (SourceTreeBenchmarkCommonCase|SourceTreeManifestExpectation|SourceTreeDeferredExpectation|SourceTreeScorecardCase|SourceTreeCombinedCase|SourceTreeCombinedPatternGroupExpectation|SourceTreeCombinedManifestShapeExpectation|SourceTreeCombinedFullyMeasuredManifestExpectation|SourceTreeCombinedManifestExpectationDefinition|SourceTreeCombinedSliceExpectation)|def (source_tree_scorecard_case_ids|source_tree_scorecard_case|source_tree_combined_target_manifest_ids|source_tree_combined_case|source_tree_combined_manifest_shape_expectation|source_tree_combined_slice_manifest_ids|source_tree_combined_slice_derived_manifest_ids|source_tree_combined_slice_expectations|source_tree_combined_fully_measured_manifest_ids|source_tree_combined_fully_measured_manifest_expectation|source_tree_combined_manifest_representative_measured_workload_ids|expected_summary_for_manifests|representative_measured_workload_ids|select_source_tree_combined_slice_rows))' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the three files above. Do not widen it into benchmark workload manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the current source-tree scorecard expectations, combined-manifest selection behavior, representative workload promotion rules, slice-selection behavior, and the current combined-suite assertion coverage.
- Do not move the combined suite's runtime assertion methods or benchmark-publication assertion logic onto the support module in this task. The point is to relocate the reusable case-definition layer, not to create a second assertion owner.

## Notes
- `RBR-1294` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1294|RBR-1295|RBR-1296" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1294`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The current simplification target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still `8202` lines long;
  - that file still defines the ten source-tree case-model dataclasses at lines `418` through `530`; and
  - it still defines the moved case-builder/query surface inline at lines `3152` through `3751` even though the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns adjacent source-tree benchmark support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `129 passed, 3471 subtests passed in 37.84s`;
  - `rg -n '^(class (SourceTreeBenchmarkCommonCase|SourceTreeManifestExpectation|SourceTreeDeferredExpectation|SourceTreeScorecardCase|SourceTreeCombinedCase|SourceTreeCombinedPatternGroupExpectation|SourceTreeCombinedManifestShapeExpectation|SourceTreeCombinedFullyMeasuredManifestExpectation|SourceTreeCombinedManifestExpectationDefinition|SourceTreeCombinedSliceExpectation)|def (source_tree_scorecard_case_ids|source_tree_scorecard_case|source_tree_combined_target_manifest_ids|source_tree_combined_case|source_tree_combined_manifest_shape_expectation|source_tree_combined_slice_manifest_ids|source_tree_combined_slice_derived_manifest_ids|source_tree_combined_slice_expectations|source_tree_combined_fully_measured_manifest_ids|source_tree_combined_fully_measured_manifest_expectation|source_tree_combined_manifest_representative_measured_workload_ids|expected_summary_for_manifests|representative_measured_workload_ids|select_source_tree_combined_slice_rows))' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports all of the local definitions listed above; and
  - `rg -n 'SourceTreeBenchmarkCommonCase|SourceTreeScorecardCase|source_tree_scorecard_case|source_tree_combined_case|source_tree_combined_slice_expectations|select_source_tree_combined_slice_rows' tests/benchmarks/source_tree_benchmark_anchor_support.py` currently returns no matches, confirming the ownership cleanup is still missing there.
