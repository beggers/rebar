## RBR-1405: Move the source-tree benchmark report contract onto owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-specific benchmark report-contract helper from `tests/benchmarks/benchmark_test_support.py`.
- `assert_source_tree_benchmark_contract(...)` still lives in shared benchmark support even though the live callers are the source-tree owner tests in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and the source-tree scorecard suite in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move that report-contract surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support stops carrying a source-tree-only report-plumbing path.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete `assert_source_tree_benchmark_contract(...)` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate `assert_source_tree_benchmark_contract(...)` on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, reusing shared helpers there only where they are still genuinely shared instead of re-exporting the moved function back through `benchmark_test_support.py`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the source-tree suites call the moved report-contract helper from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the shared-support ownership assertions stop allowing `assert_source_tree_benchmark_contract` as a benchmark-test-support-owned routed reference and instead verify the tighter owner boundary.
- Do not widen into the generic manifest-contract helpers, benchmark summary helpers, benchmark manifest loaders, or non-source-tree benchmark owner surfaces in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_report_contract_accepts_single_manifest_native_loaded_scorecard or source_tree_report_contract_accepts_combined_manifest_scorecard_without_native_load'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_runner_regenerates_source_tree_scorecards`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_combined_route_helper'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def assert_source_tree_benchmark_contract' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "rg -n '^def assert_source_tree_benchmark_contract' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the existing source-tree-only report contract onto the existing owner module over adding another neutral helper module, wrapper, or routing layer.
- Keep the run bounded to this owner-boundary cleanup; do not also move `_artifact_manifest_record(...)`, `_assert_benchmark_summary_consistent(...)`, or broader shared report helpers unless the moved owner helper still needs to call them in place.
- Do not change benchmark workload files, generated reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1405|1405' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` found no reserved future-id use in tracked state and no ready/in-progress/blocked duplicate for `RBR-1405`; the only matches were historical numeric mentions inside completed task notes.
- Candidate selection in this run:
  - With both tracked and live JSON counts at zero, I inspected the remaining benchmark-support ownership seams under `tests/benchmarks/` instead of widening into JSON work.
  - `rg -n 'assert_source_tree_benchmark_contract\\(|_artifact_manifest_record\\(|_assert_benchmark_summary_consistent\\(' tests -g '*.py'` shows that `assert_source_tree_benchmark_contract(...)` is only consumed by source-tree benchmark suites, while the lower-level summary and manifest-record helpers still have test-local direct coverage and can remain shared.
  - That makes the source-tree report-contract surface a bounded post-JSON owner-boundary cleanup with a clear cross-file payoff: one fewer source-tree-only report-plumbing path in shared support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_report_contract_accepts_single_manifest_native_loaded_scorecard or source_tree_report_contract_accepts_combined_manifest_scorecard_without_native_load'` passed with `2 passed, 118 deselected in 0.12s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_runner_regenerates_source_tree_scorecards` passed with `1 passed, 444 subtests passed in 1.86s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_combined_route_helper'` passed with `5 passed, 175 deselected in 0.17s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n '^def assert_source_tree_benchmark_contract' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently reports the exact shared-support seam this task is intended to remove: the definition still exists only in `tests/benchmarks/benchmark_test_support.py`.

## Completion
- Moved `assert_source_tree_benchmark_contract(...)` out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, keeping `_assert_benchmark_summary_consistent(...)` and `_artifact_manifest_record(...)` shared in place.
- Updated the source-tree benchmark suites to call the owner helper through `source_tree_benchmark_anchor_support`, and tightened the ownership assertions so `assert_source_tree_benchmark_contract` is no longer treated as a `benchmark_test_support`-owned route.
- Verified with the task pytest targets, targeted owner-boundary pytest coverage, `py_compile`, and `rg` checks confirming the helper definition no longer exists in `tests/benchmarks/benchmark_test_support.py` and now exists in `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
