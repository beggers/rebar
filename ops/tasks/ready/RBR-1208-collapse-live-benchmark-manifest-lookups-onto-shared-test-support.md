# RBR-1208: Collapse live benchmark manifest lookups onto shared test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining duplicated live-manifest lookup helpers and inline `workloads_by_id` maps that still span the benchmark support tests and the giant combined boundary benchmark suite by consolidating them onto one shared benchmark test-support path, so benchmark tests stop hand-rolling the same `load_manifest(...).workloads` indexing logic in multiple places.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_contract_benchmark_support.py`
- `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` with one shared live-manifest lookup surface that covers the current benchmark test shapes without adding another `*_support.py` module:
  - it must load ordinary `rebar_harness.benchmarks.Workload` objects from tracked benchmark manifest files through the existing `load_manifest(...)` path rather than inventing a new intermediate representation;
  - it must support direct single-workload lookup for the current support tests; and
  - it must support ordered multi-workload lookup by explicit workload id so the current combined-suite slice helpers can keep their existing ordering contracts.
- Refactor the small benchmark support tests to use that shared helper and delete their local manifest-lookup wrappers instead of leaving thin aliases behind:
  - `tests/benchmarks/test_source_tree_contract_benchmark_support.py`: `_manifest_workload_by_id`
  - `tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py`: `_manifest_workloads_by_id`
  - `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`: `_manifest_workload`
  - `tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py`: `_manifest_workload`
- Replace the inline `workloads_by_id = {...}` map-building blocks in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the shared helper path while keeping the existing helper/test surface intact:
  - `_conditional_group_exists_callable_bytes_slice_workloads`
  - `_conditional_group_exists_quantified_callable_str_workloads`
  - `_conditional_group_exists_nested_callable_str_workloads`
  - `_conditional_group_exists_nested_callable_bytes_workloads`
  - `_conditional_group_exists_quantified_callable_bytes_workloads`
  - `_conditional_group_exists_alternation_callable_bytes_workloads`
  - `_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads`
- Preserve the current benchmark-contract behavior exactly:
  - keep the current manifest filenames, workload ids, ordering, bytes-only filtering, and expectation-driven workload selection unchanged;
  - keep the current test names, parameter ids, and assertion surfaces unchanged apart from routing lookup through the shared helper;
  - do not change benchmark workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops/state prose; and
  - do not widen this into another extraction pass from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` beyond the manifest-lookup plumbing named above.
- Reuse the existing `tests/benchmarks/benchmark_test_support.py` owner instead of adding a new architectural layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes or nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads'`
- `bash -lc "! rg -n 'def _manifest_workload_by_id\\(|def _manifest_workloads_by_id\\(|^def _manifest_workload\\(|workloads_by_id = \\{' tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1208` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1208|RBR-1209|RBR-1210" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both `RBR-1206` and `RBR-1207` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `15917` lines in this run;
  - `bash -lc "! rg -n 'def _manifest_workload_by_id\\(|def _manifest_workloads_by_id\\(|^def _manifest_workload\\(|workloads_by_id = \\{' tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails exactly on the duplicated lookup helpers and inline manifest maps named above; and
  - the remaining matches sit in the four small support tests plus the seven inline helper blocks in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_grouped_alternation_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_compiled_pattern_contract_benchmark_support.py` returned `65 passed in 0.16s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes or nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads'` returned `18 passed, 434 deselected, 64 subtests passed in 0.21s`; and
  - the negative `rg` check named above currently fails exactly because those duplicated live-manifest lookup helpers are still present in this checkout.
