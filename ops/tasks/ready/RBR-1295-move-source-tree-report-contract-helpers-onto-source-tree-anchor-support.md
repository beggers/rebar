# RBR-1295: Move source-tree report contract helpers onto source-tree anchor support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining reusable source-tree report-contract assertion layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` owner, so the giant combined benchmark suite stops carrying both the benchmark assertions and the generic scorecard/manifest contract helpers those assertions share.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it owns the reusable source-tree report-contract helper surface that currently lives inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including these functions:
  - `_assert_benchmark_summary_consistent`
  - `_artifact_manifest_record`
  - `assert_source_tree_benchmark_contract`
  - `assert_benchmark_manifest_contract`
  - `find_manifest_record`
- Move any small import or helper dependency that the moved functions need onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, while preserving the current behavior and contract checks:
  - keep the summary-key validation, baseline/implementation metadata checks, artifact manifest-record checks, per-manifest selection-mode checks, and manifest-record lookup behavior intact;
  - preserve the current use of `build_cpython_baseline(version_family="3.12.x")`; and
  - keep the helper API callable from the combined suite without introducing a new wrapper or broker module.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved report-contract helpers from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of defining them locally. After the cleanup, the combined suite should keep only benchmark assertions and test-local workload-selection helpers that are still specific to that suite.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it pins the slimmer ownership boundary directly:
  - assert the moved report-contract helpers are exposed from `tests.benchmarks.source_tree_benchmark_anchor_support`;
  - assert `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines those five top-level helpers locally; and
  - keep the existing source-tree anchor-support assertions green.
- Do not add a new helper broker module for this task. Reuse `tests/benchmarks/source_tree_benchmark_anchor_support.py` as the owner for the moved report-contract helper layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record))' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the three files above. Do not widen it into benchmark workload manifests, benchmark runner behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Preserve the current source-tree benchmark metadata checks, combined-suite artifact expectations, per-manifest selection/readiness assertions, and the current benchmark-publication assertion coverage.
- Do not move the suite's conditional/callable workload-selection helpers or its runtime benchmark assertion methods in this task. The point is to relocate the shared report-contract helper layer, not to re-plan the entire combined suite.

## Notes
- `RBR-1295` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1295|RBR-1296|RBR-1297" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1295`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The current simplification target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still `4885` lines long;
  - that file still defines the five report-contract helpers listed above locally at lines `192` through `437`; and
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` currently has no definitions for those helper names even though it already owns the adjacent source-tree manifest/scorecard support API the helpers validate against.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `134 passed, 3471 subtests passed in 37.88s`;
  - `rg -n '^(def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record))' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports all five local definitions, confirming the ownership cleanup is still missing there; and
  - `rg -n '(_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` currently returns no matches, confirming the support-module ownership cleanup is still missing.
