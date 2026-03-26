## RBR-1431: Collapse publication-runtime synthetic benchmark builders onto shared support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the publication-runtime test module's private synthetic benchmark builder family and route those synthetic workloads/manifests through the existing shared benchmark support synthesis layer instead.
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still carries its own `_summary_contract_workload_payload(...)`, `_summary_contract_workload_record(...)`, and `_summary_contract_manifest(...)` stack even though `tests/benchmarks/benchmark_test_support.py` already owns reusable synthetic workload/manifest helpers for benchmark-only contract tests.
- Keep the shared support module as the one legible place that owns benchmark-test synthesis primitives; keep the publication-runtime suite focused on scorecard/runtime assertions rather than a second copy of synthetic workload plumbing.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` only as needed so it can build the synthetic workload rows and tiny `BenchmarkManifest` objects that `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` currently synthesizes locally for summary-contract coverage.
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` to delete its local duplicate builder layer:
  - `_summary_contract_workload_payload(...)`
  - `_summary_contract_workload_record(...)`
  - `_summary_contract_manifest(...)`
- Keep the publication-runtime suite's behavior and assertions intact while routing those cases through shared support helpers.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it asserts the tighter ownership boundary:
  - the shared support module exports the surviving synthetic benchmark builder surface used by publication-runtime tests
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` no longer defines the deleted `_summary_contract_*` helpers locally
- Keep the run bounded to this consolidation:
  - do not change benchmark manifests, harness/runtime behavior, reports, or tracked project-state files
  - do not move unrelated publication-runtime assertions or source-tree scorecard helpers

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py -k 'build_family_summary or build_manifest_summaries or publication_runtime or synthetic_workload'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^def _summary_contract_workload_payload\\(|^def _summary_contract_workload_record\\(|^def _summary_contract_manifest\\(' tests/benchmarks/test_benchmark_publication_runtime_contracts.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1431|RBR-1432|RBR-1433|RBR-1434|RBR-1435" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1431` was available.
- Candidate selection in this run:
  - The first probe, `_assert_benchmark_summary_consistent(...)` plus `_artifact_manifest_record(...)` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, was no longer a good post-JSON architecture target because those helpers already live entirely inside the source-tree owner suite and do not represent a remaining shared layer.
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still defines `_summary_contract_workload_payload(...)`, `_summary_contract_workload_record(...)`, and `_summary_contract_manifest(...)`, and `rg -n "_summary_contract_workload_payload|_summary_contract_workload_record|_summary_contract_manifest" tests/benchmarks/test_benchmark_publication_runtime_contracts.py` showed that stack is only used inside that module.
  - `tests/benchmarks/benchmark_test_support.py` already owns adjacent synthetic benchmark helpers such as `synthetic_workload(...)`, `_synthetic_manifest(...)`, `_synthetic_workload(...)`, and `_synthetic_manifest_loader(...)`, so consolidating publication-runtime synthesis onto that existing support layer removes a duplicate benchmark-test builder family instead of inventing a new abstraction.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py -k 'build_family_summary or build_manifest_summaries or publication_runtime or synthetic_workload'` passed with `191 passed, 3 skipped, 194 deselected in 0.41s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py` passed.
  - `bash -lc "rg -n '^def _summary_contract_workload_payload\\(|^def _summary_contract_workload_record\\(|^def _summary_contract_manifest\\(' tests/benchmarks/test_benchmark_publication_runtime_contracts.py"` currently finds the duplicate local builder family this task deletes.
