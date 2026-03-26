## RBR-1389: Delete source-tree zero-gap assertion helpers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two zero-gap assertion wrappers from the shared source-tree benchmark owner layer, and have the affected tests assert those zero-gap contracts directly from the stored manifest expectations, `source_tree_combined_case(...)`, and `benchmark_test_support.assert_zero_gap_manifest_workloads_measured(...)` instead of routing through helper methods.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove these helper functions from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without replacing them with another alias, wrapper, or shared helper layer:
  - `assert_zero_gap_bytes_representative_subset`
  - `assert_zero_gap_manifest_representative_promotion`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the current zero-gap representative-promotion and bytes-subset checks keep the same behavioral coverage through direct reads of the existing owner data:
  - promotion checks must read the relevant definition directly from `source_tree_support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]`, assert the same zero-gap manifest-expectation fields through `source_tree_support.source_tree_combined_case(manifest_id)`, and keep using `benchmark_test_support.assert_zero_gap_manifest_workloads_measured(...)` with the same selected-workload counts;
  - bytes-subset checks must keep asserting membership in `zero_gap_bytes_representative_subsets`, keep validating public representative rows through `source_tree_support.source_tree_combined_manifest_representative_measured_workload_ids(manifest_id)`, and keep the same measured-row count checks without routing through a source-tree support assertion wrapper.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it treats the deleted helpers as absent from the source-tree support module, and rewrite the current helper-behavior tests to target the direct benchmark-support assertion call shape or the remaining public owner data instead of calling the deleted wrappers.
- Do not change benchmark manifests, workload ids, selected-workload ordering, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'assert_zero_gap_bytes_representative_subset or assert_zero_gap_manifest_representative_promotion or promote_zero_gap_representatives or zero_gap_bytes'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'def assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(|source_tree_support\\.assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(|support\\.assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer direct reads of the stored source-tree expectation data plus the existing shared `benchmark_test_support.assert_zero_gap_manifest_workloads_measured(...)` assertion over another owner-local helper.
- Keep the run bounded to deleting these two wrappers and rewiring their current source-tree support and combined-boundary test consumers; do not reopen broader `source_tree_combined_case(...)`, slice-row, or representative-id helper cleanup in the same task.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1389|RBR-1390|RBR-1391|RBR-1392' ops/state/current_status.md ops/state/backlog.md` returned no reserved future id hits for `RBR-1389`.
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this checkout, so there was no ready or blocked duplicate to refine or reopen first.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - With tracked and live JSON counts both at zero, I first inspected `source_tree_combined_manifest_representative_measured_workload_ids(...)`, but it still owns real merge logic across explicit manifest representatives, shape expectations, and slice expectations, so deleting it would spill across too many call sites for one bounded run.
  - `assert_zero_gap_bytes_representative_subset(...)` and `assert_zero_gap_manifest_representative_promotion(...)` are smaller owner-surface wrappers: they centralize direct reads of `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `source_tree_combined_case(...)`, and one shared benchmark-support assertion, and their live consumers stay bounded to the source-tree support tests plus the combined source-tree benchmark suite.
  - Deleting those two helpers removes one more source-tree owner wrapper layer without changing the runtime benchmark harness or any published benchmark artifacts.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'assert_zero_gap_bytes_representative_subset or assert_zero_gap_manifest_representative_promotion or promote_zero_gap_representatives or zero_gap_bytes'` passed with `3 passed, 386 deselected, 393 subtests passed in 3.68s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n 'def assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(|source_tree_support\\.assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(|support\\.assert_zero_gap_(bytes_representative_subset|manifest_representative_promotion)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact helper definitions and call sites this task is intended to delete.
