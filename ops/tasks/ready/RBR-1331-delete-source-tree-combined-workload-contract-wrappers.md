## RBR-1331: Delete source-tree combined workload contract wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining class-local workload-contract wrapper layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared benchmark contract helpers live in `tests/benchmarks/benchmark_test_support.py` instead of being reimplemented inside the combined-suite test class.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` with one canonical shared helper for asserting manifest workload contracts across a scorecard/manifest pair:
  - it must cover the loop that currently calls `find_workload_record(...)`, `find_workload_document(...)`, and `assert_benchmark_workload_contract(...)` for a sequence of `(workload_id, expected_status)` pairs
  - it must preserve the optional subtest labeling behavior that `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_manifest_workload_contracts(...)` currently provides
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to reuse shared support helpers instead of keeping class-local wrappers for:
  - `_assert_manifest_workload_contracts(...)`
  - `_assert_zero_gap_manifest_workloads_measured(...)`
- Reuse the already-shared `benchmark_test_support.assert_zero_gap_manifest_workloads_measured(...)` surface everywhere the combined suite currently funnels through its private `_assert_zero_gap_manifest_workloads_measured(...)` wrapper.
- Add or update focused support-surface coverage in `tests/benchmarks/test_benchmark_test_support.py` so the cleanup stays pinned:
  - prove the shared helper exists on `benchmark_test_support`
  - fail if `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reintroduces either deleted wrapper method
- Do not add a new helper module, owner alias shim, or another wrapper layer.
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not move broader source-tree scorecard or slice-selection logic out of the combined suite

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^    def (_assert_manifest_workload_contracts|_assert_zero_gap_manifest_workloads_measured)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`

## Constraints
- Keep the task bounded to deleting the source-tree combined suite's local workload-contract wrappers and consolidating that logic onto the existing shared benchmark support surface.
- Prefer deleting consumer-local wrappers over introducing another indirection layer.

## Notes
- `RBR-1331` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1331|RBR-1332|RBR-1333|RBR-1334|RBR-1335" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines class-local `_assert_manifest_workload_contracts(...)` and `_assert_zero_gap_manifest_workloads_measured(...)`
  - `tests/benchmarks/benchmark_test_support.py` already owns `find_workload_record(...)`, `find_workload_document(...)`, `assert_benchmark_workload_contract(...)`, and `assert_zero_gap_manifest_workloads_measured(...)`, so the combined suite is carrying a redundant local wrapper layer rather than a missing shared primitive
  - the combined suite still calls those local wrappers repeatedly across zero-gap and representative-workload assertions
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `466 passed, 2264 subtests passed in 13.31s`
  - `bash -lc "! rg -n '^    def (_assert_manifest_workload_contracts|_assert_zero_gap_manifest_workloads_measured)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those class-local wrappers still exist, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
