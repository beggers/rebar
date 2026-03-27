## RBR-1443: Localize benchmark runtime assertion helpers onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining shared benchmark-runtime assertion layer from `tests/benchmarks/benchmark_test_support.py`, where owner suites still route CPython workload execution and result-parity assertions through shared support.
- Keep `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` responsible for their own runtime assertion helpers so shared support stays focused on manifest lookup, temporary manifest writing, and cache clearing.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it no longer calls `benchmark_test_support.run_benchmark_workload_with_cpython` or `benchmark_test_support.assert_benchmark_workload_matches_expected_result`.
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it no longer calls `benchmark_test_support.run_benchmark_workload_with_cpython` or `benchmark_test_support.assert_benchmark_workload_matches_expected_result`.
- Remove `run_benchmark_workload_with_cpython()` and `assert_benchmark_workload_matches_expected_result()` from `tests/benchmarks/benchmark_test_support.py`, along with any imports that only supported those helpers.
- Tighten `tests/benchmarks/test_benchmark_test_support.py` so the shared-support contract asserts those runtime assertion helpers stay owner-local and so the anchored-parity tests patch the owner-suite helpers directly instead of the shared-support exports.
- Keep the run bounded to this shared-layer deletion:
  - do not move or rewrite `manifest_workloads()`, `live_manifest_workload()`, `live_manifest_workloads()`, `_write_test_manifest()`, or `_clear_anchor_support_caches()`
  - do not change benchmark manifests, harness runtime behavior, reports, `tests/python/fixture_parity_support.py`, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'publication_runtime_contracts or anchored_workload_case_result_parity or benchmark_manifest_validation'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'callback_results or round_trip_preserves_callback_results or runtime_contract_span'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'anchored_workload_case_result_parity or callback_results or module_helper_keyword_contract_workloads'`
- `bash -lc "! rg -n 'benchmark_test_support\\.(run_benchmark_workload_with_cpython|assert_benchmark_workload_matches_expected_result)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py"`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1443|RBR-1444|RBR-1445" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1443` was available.
- Candidate selection in this run:
  - A live reference scan showed `run_benchmark_workload_with_cpython()` and `assert_benchmark_workload_matches_expected_result()` are consumed only by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`.
  - Removing those two helpers also lets `tests/benchmarks/benchmark_test_support.py` drop its remaining `re` import plus the `assert_pattern_parity` and `assert_match_result_parity` fixture-parity imports, shrinking shared benchmark support to manifest-oriented helpers.
  - `tests/benchmarks/test_benchmark_manifest_validation.py` still uses only `_write_test_manifest()` from shared benchmark support, so this cleanup can stay bounded to the owner-only runtime assertion layer instead of widening into manifest helper changes.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'publication_runtime_contracts or anchored_workload_case_result_parity or benchmark_manifest_validation'` passed (`5 passed, 218 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'callback_results or round_trip_preserves_callback_results or runtime_contract_span'` passed (`5 passed, 190 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'anchored_workload_case_result_parity or callback_results or module_helper_keyword_contract_workloads'` passed (`42 passed, 271 deselected`).
  - `bash -lc "! rg -n 'benchmark_test_support\\.(run_benchmark_workload_with_cpython|assert_benchmark_workload_matches_expected_result)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py"` is currently red because both owner suites still route through the shared helper layer this task deletes.
