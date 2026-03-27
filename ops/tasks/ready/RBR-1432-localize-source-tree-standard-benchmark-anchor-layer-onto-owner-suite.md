## RBR-1432: Localize source-tree standard benchmark anchor layer onto owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining source-tree standard-benchmark anchor-definition layer from `tests/benchmarks/benchmark_test_support.py` and keep that owner-specific contract machinery inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- `tests/benchmarks/benchmark_test_support.py` still owns the `StandardBenchmarkAnchorContractDefinition` type plus the anchor-definition, anchored/unanchored pairing, zero-gap, and parametrization helpers that are consumed by the source-tree combined boundary suite rather than by multiple independent benchmark suites.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on benchmark helpers that are actually shared across benchmark test modules, and keep the source-tree owner suite responsible for its own standard-benchmark anchor inventory and contract plumbing.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move the source-tree-only standard-benchmark anchor layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including the surviving contract type and helper stack that only serves the source-tree owner suite:
  - `StandardBenchmarkAnchorContractDefinition`
  - `_definition_anchor_expectations(...)`
  - `_workload_case_pair_anchor_expectations(...)`
  - `published_case_ids_by_signature(...)`
  - `anchored_workload_case_ids(...)`
  - `unanchored_workload_ids(...)`
  - `expected_anchored_workload_case_pairs(...)`
  - `assert_anchored_workload_case_result_parity(...)`
  - `assert_zero_gap_manifest_workloads_measured(...)`
  - the `_standard_benchmark_*` parametrization helpers that currently exist only to drive the owner suite
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it owns and uses that localized layer directly instead of routing through `tests.benchmarks.benchmark_test_support`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it stops treating the deleted source-tree-only anchor layer as shared support surface and instead asserts the tighter ownership boundary.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move benchmark-test helpers that still have real cross-suite consumers such as manifest writing, CPython workload execution, or publication-runtime synthetic manifest builders

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark or anchored_workload or unanchored_workload or zero_gap_manifest or published_case_ids_by_signature' -q`
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark or anchored_workload or unanchored_workload or published_case_ids_by_signature or zero_gap_manifest' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n 'StandardBenchmarkAnchorContractDefinition|_definition_anchor_expectations|_workload_case_pair_anchor_expectations|published_case_ids_by_signature|anchored_workload_case_ids|unanchored_workload_ids|expected_anchored_workload_case_pairs|assert_anchored_workload_case_result_parity|assert_zero_gap_manifest_workloads_measured|_standard_benchmark_' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1432|RBR-1433|RBR-1434|RBR-1435" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1432` was available.
- Candidate selection in this run:
  - The first probe showed that `_summary_contract_workload_payload(...)`, `_summary_contract_workload_record(...)`, and `_summary_contract_manifest(...)` are now publication-runtime-only helpers in `tests/benchmarks/benchmark_test_support.py`, but immediately reversing `RBR-1431` would create avoidable queue churn instead of removing a clearly older surviving owner layer.
  - The second probe showed that the standard-benchmark anchor-definition layer still lives in `tests/benchmarks/benchmark_test_support.py` even though its substantive consumers are the source-tree combined owner suite and the support meta-tests for that same layer.
  - `rg -n 'StandardBenchmarkAnchorContractDefinition|_definition_anchor_expectations|_workload_case_pair_anchor_expectations|published_case_ids_by_signature|anchored_workload_case_ids|unanchored_workload_ids|expected_anchored_workload_case_pairs|assert_anchored_workload_case_result_parity|assert_zero_gap_manifest_workloads_measured|_standard_benchmark_' tests/benchmarks/benchmark_test_support.py` showed the remaining owner-specific layer still concentrated in shared support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark or anchored_workload or unanchored_workload or zero_gap_manifest or published_case_ids_by_signature' -q` passed with `23 passed, 284 deselected, 4 subtests passed in 0.45s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark or anchored_workload or unanchored_workload or published_case_ids_by_signature or zero_gap_manifest' -q` passed with `24 passed, 175 deselected in 0.25s`.
  - The `rg` check above currently finds the source-tree-only anchor layer in `tests/benchmarks/benchmark_test_support.py`; that red state belongs to the exact cleanup this task queues.
