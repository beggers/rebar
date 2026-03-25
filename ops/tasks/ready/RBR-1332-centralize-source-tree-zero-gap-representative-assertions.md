## RBR-1332: Centralize source-tree zero-gap representative assertions

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining class-local zero-gap representative assertion wrappers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the source-tree combined benchmark owner module owns that support surface instead of the monolithic suite class.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` with canonical testcase-oriented helpers for the two remaining combined-suite zero-gap representative assertion flows:
  - the bytes representative-subset assertion currently implemented by `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_zero_gap_bytes_representative_subset(...)`
  - the representative-promotion assertion currently implemented by `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_zero_gap_manifest_representative_promotion(...)`
- Keep those helpers owner-scoped:
  - they should live on `source_tree_benchmark_anchor_support`, not on `benchmark_test_support`
  - they should keep using the existing source-tree combined case/expectation APIs plus `benchmark_test_support.assert_zero_gap_manifest_workloads_measured(...)`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to call the shared owner helpers directly and delete both class-local wrapper methods:
  - `_assert_zero_gap_bytes_representative_subset(...)`
  - `_assert_zero_gap_manifest_representative_promotion(...)`
- Add or update focused coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the cleanup stays pinned:
  - prove the new helper surface exists on `source_tree_benchmark_anchor_support`
  - fail if `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reintroduces either deleted wrapper method
- Do not add a new helper module, alias shim, or another wrapper layer.
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not move broader combined-suite selection/report contract logic out of the owner module in the same task

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^    def (_assert_zero_gap_bytes_representative_subset|_assert_zero_gap_manifest_representative_promotion)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Constraints
- Keep the task bounded to centralizing the combined source-tree suite's two remaining zero-gap representative assertion wrappers onto the existing owner support module.
- Prefer deleting consumer-local wrappers over adding another indirection layer.

## Notes
- `RBR-1332` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1332|RBR-1333|RBR-1334|RBR-1335" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `_assert_zero_gap_bytes_representative_subset(...)` and `_assert_zero_gap_manifest_representative_promotion(...)`
  - both wrappers are source-tree-owner-specific and are only called from the combined suite, so they belong on `tests/benchmarks/source_tree_benchmark_anchor_support.py` rather than inside the test class
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the adjacent source-tree combined expectation/case/report helper surface those wrappers consume
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `342 passed, 1807 subtests passed in 13.00s`
  - `bash -lc "! rg -n '^    def (_assert_zero_gap_bytes_representative_subset|_assert_zero_gap_manifest_representative_promotion)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those class-local wrappers still exist, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
