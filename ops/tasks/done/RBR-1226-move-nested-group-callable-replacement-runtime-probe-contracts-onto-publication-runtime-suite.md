# RBR-1226: Move nested-group callable replacement runtime-probe contracts onto publication-runtime suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the stranded runtime-only nested-group callable-replacement bytes block that still lives at the bottom of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing runtime-contract owner in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the giant combined benchmark suite stops owning payload round-trip and `run_internal_workload_probe(...)` coverage that does not depend on its broader scorecard or manifest-selection assertions.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it becomes the owner for the current nested-group callable-replacement bytes runtime block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move this existing helper-and-test block into that dedicated runtime-contract file without widening its scope or changing its assertion surface:
  - `_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads(...)`
  - `_NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_BACKREFERENCE_BYTES_WORKLOAD_PARAMS`
  - `test_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results`
  - `test_run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads`
- Keep the extracted runtime surface pinned to current live behavior exactly:
  - preserve the current workload selection logic for the `nested-group-callable-replacement-boundary` manifest's `quantified-branch-local-backreference` slice, including the existing `-bytes` workload filter against `source_tree_combined_slice_expectations(...)`;
  - preserve the existing `workload_to_payload(...)` / `workload_from_payload(...)` round-trip contract exactly for those selected bytes workloads, including the same `text_model`, `pattern_payload()`, `haystack_payload()`, and `assert_benchmark_workload_matches_expected_result(...)` expectations; and
  - preserve the current `run_internal_workload_probe(...)` coverage exactly for both `("re", "cpython.re")` and `("rebar", "rebar")`, including the same sorted JSON payload serialization and the same measured-status plus positive-`median_ns` assertions.
- Reuse the existing runtime-contract suite instead of adding another layer:
  - keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` as the owner for this extracted block;
  - keep using the existing benchmark helpers already in the test tree rather than importing the giant combined suite into the runtime-contract suite; and
  - do not add a new `*_support.py` module, a new sibling runtime contract suite, or wrappers/aliases left behind in the combined suite.
- Delete the moved helper and tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads'`
- `bash -lc "! rg -n 'def test_(nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results|run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Completed 2026-03-24: moved the bounded nested-group callable-replacement bytes runtime helper and both probe/round-trip tests into `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, deleted the duplicate block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and kept the existing bytes-only slice selection, payload round-trip, and `run_internal_workload_probe(...)` assertions unchanged.
- `RBR-1226` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/` currently contains only `RBR-1225`, and `ops/tasks/in_progress/` plus `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1226|RBR-1227|RBR-1228" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation or sibling task at `RBR-1226`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout and `.rebar/runtime/dashboard.md` reports `Recent Blocked Tasks: none`.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle completed both `RBR-1223` and `RBR-1224` through the normal done path with no inherited-dirty checkpoint churn or stalled refresh/commit anomaly.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still `11112` lines in this run, while `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` is `1230` lines;
  - `rg -n "nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads|run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads|round_trip_preserves_callback_results" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` currently matches only the combined-suite copies at lines `8925`, `8955`, and `8983`; and
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` already owns adjacent `workload_to_payload(...)`, `workload_from_payload(...)`, and `run_internal_workload_probe(...)` contracts, so this cleanup removes another runtime-only block from the giant combined suite instead of introducing another owner.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads'` returned `12 passed, 138 deselected in 0.16s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those two tests still live in the combined suite.
