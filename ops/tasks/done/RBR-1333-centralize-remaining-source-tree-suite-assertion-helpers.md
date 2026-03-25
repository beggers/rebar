## RBR-1333: Centralize remaining source-tree suite assertion helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining class-local source-tree assertion helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the source-tree owner module owns that support surface instead of the monolithic suite classes.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` with canonical testcase-oriented helpers for the four remaining class-local assertion flows currently implemented in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_source_tree_combined_manifest_slice(...)`
  - `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_source_tree_combined_pattern_group(...)`
  - `SourceTreeScorecardBenchmarkSuiteTest._assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(...)`
  - `SourceTreeScorecardBenchmarkSuiteTest._assert_zero_gap_representative_workload_subset(...)`
- Keep those helpers owner-scoped:
  - they should live on `source_tree_benchmark_anchor_support`, not on `benchmark_test_support`
  - they should keep using the existing source-tree combined case, manifest-expectation, and slice-selection APIs instead of introducing a new helper layer
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to call the shared owner helpers directly and delete all four class-local wrapper methods named above.
- Add or update focused coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the cleanup stays pinned:
  - prove the new helper surface exists on `source_tree_benchmark_anchor_support`
  - fail if `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reintroduces any of the four deleted wrapper methods
- Do not add a new helper module, alias shim, or another wrapper layer.
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not move broader source-tree benchmark routing or compiled-pattern contract plumbing out of the owner module in the same task

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^    def (_assert_source_tree_combined_manifest_slice|_assert_source_tree_combined_pattern_group|_assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation|_assert_zero_gap_representative_workload_subset)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Constraints
- Keep the task bounded to centralizing the four remaining source-tree owner assertion helpers onto the existing owner support module.
- Prefer deleting consumer-local wrappers over adding another indirection layer.

## Notes
- `RBR-1333` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1333|RBR-1334|RBR-1335|RBR-1336" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines exactly four class-local `_assert_*` helpers, and each one is source-tree-owner-specific rather than generic `unittest` scaffolding
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the adjacent source-tree manifest, scorecard, and contract helper surface those methods consume
  - centralizing these four helpers would leave the monolithic suite focused on test cases instead of support plumbing
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `346 passed, 1821 subtests passed in 13.02s`
  - `bash -lc "! rg -n '^    def (_assert_source_tree_combined_manifest_slice|_assert_source_tree_combined_pattern_group|_assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation|_assert_zero_gap_representative_workload_subset)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those class-local wrappers still exist, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed

## Completion
- Landed 2026-03-25: centralized the remaining combined-suite manifest-slice, pattern-group, single-manifest zero-gap scorecard, and zero-gap representative-subset assertion helpers onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, then routed `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` through those owner helpers and deleted the four class-local wrapper methods.
- Added focused support-contract coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the owner helper surface is asserted on `source_tree_benchmark_anchor_support` and the combined-suite AST checks fail if any of the four deleted wrapper methods return.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` (`347 passed, 1821 subtests passed in 13.21s`), the required `rg` wrapper-definition check, and `python3 -m py_compile` on the three touched benchmark files.
