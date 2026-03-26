## RBR-1420: Delete the single-consumer source-tree scorecard wrapper layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the `source_tree_scorecard_case` wrapper layer from `tests/benchmarks/source_tree_benchmark_anchor_support.py` now that it is only consumed by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The remaining `SourceTreeScorecardCase` / `_SourceTreeScorecardDefinition` / `SOURCE_TREE_SCORECARD_EXPECTATIONS` path duplicates manifest-selection and expectation shaping that the combined benchmark suite can derive from the surviving `source_tree_combined_case` and manifest-level expectation helpers.
- Leave the benchmark test stack with one fewer bespoke report-contract layer after the JSON burn-down: the source-tree support module should keep shared manifest-expectation primitives, and the combined boundary suite should own any suite-local grouping or ordering expectations it still needs.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete the single-consumer scorecard wrapper surface from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `SourceTreeScorecardCase`
  - `_SourceTreeScorecardDefinition`
  - `SOURCE_TREE_SCORECARD_EXPECTATIONS`
  - `source_tree_scorecard_case`
- Keep `SourceTreeManifestExpectation`, `source_tree_combined_case`, `source_tree_combined_target_manifest_ids`, `expected_summary_for_manifests`, and the surviving manifest/slice helpers intact where they are still genuinely shared across benchmark support and suite code.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it derives its expected combined-report assertions from the surviving shared manifest helpers plus suite-local helpers, instead of calling `source_tree_scorecard_case(...)` or iterating `SOURCE_TREE_SCORECARD_EXPECTATIONS`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_test_support.py` so they stop asserting that the deleted scorecard wrapper exports or aliases remain present, and instead assert that the surviving support surface stays package-routed without that extra layer.
- Keep the task bounded to deleting that wrapper path; do not reopen benchmark workload manifests, `rebar_harness/benchmarks.py`, reporting/status files, or broader `source_tree_benchmark_anchor_support.py` decomposition beyond what the wrapper removal requires.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'SourceTreeScorecardCase|_SourceTreeScorecardDefinition|SOURCE_TREE_SCORECARD_EXPECTATIONS|source_tree_scorecard_case\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"`

## Completion
- Deleted `SourceTreeScorecardCase`, `_SourceTreeScorecardDefinition`, `SOURCE_TREE_SCORECARD_EXPECTATIONS`, and `source_tree_scorecard_case(...)` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Rebuilt the scorecard-case expectations locally inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the suite now derives combined-report assertions from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `source_tree_combined_manifest_representative_measured_workload_ids(...)`, and `expected_summary_for_manifests(...)` without the extra shared wrapper layer.
- Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_test_support.py` so the package-surface assertions now cover only the surviving shared source-tree support surface.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `670 passed, 1573 subtests passed in 14.82s`.
  - `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'SourceTreeScorecardCase|_SourceTreeScorecardDefinition|SOURCE_TREE_SCORECARD_EXPECTATIONS|source_tree_scorecard_case\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` passed.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` had no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1420|RBR-1421|RBR-1422" ops/state/current_status.md ops/state/backlog.md` found no reserved future-id use for `RBR-1420`.
- Candidate selection in this run:
  - First probe: `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` is only imported by `tests/benchmarks/test_benchmark_test_support.py`, but that looked like a file merge more than a clear shared-layer deletion.
  - Second probe: `source_tree_scorecard_case(...)` is referenced only inside `tests/benchmarks/source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, while `test_source_tree_combined_boundary_benchmarks.py` already uses `source_tree_combined_case(...)` more broadly (`56` direct calls versus `34` scorecard-wrapper calls in this checkout).
  - That makes the scorecard wrapper path the smaller architectural removal: one single-consumer support layer can disappear without reopening manifests or benchmark runner behavior.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `670 passed, 1573 subtests passed in 14.36s`.
  - `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'SourceTreeScorecardCase|_SourceTreeScorecardDefinition|SOURCE_TREE_SCORECARD_EXPECTATIONS|source_tree_scorecard_case\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` currently fails only because the scorecard wrapper layer is still present, which is the exact cleanup this task queues.
