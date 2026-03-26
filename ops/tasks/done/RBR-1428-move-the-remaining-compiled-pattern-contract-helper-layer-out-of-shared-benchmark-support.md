## RBR-1428: Move the remaining compiled-pattern contract helper layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining owner-only compiled-pattern contract helper layer from `tests/benchmarks/benchmark_test_support.py`.
- After `RBR-1427`, shared benchmark support still owns `compiled_pattern_contract_expected_build_calls(...)`, `_run_cpython_compiled_pattern_module_helper_workload(...)`, `_assert_wrong_text_model_payload_round_trip(...)`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`, and `include_live_compiled_pattern_module_success_workload(...)` even though the only live consumer path is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the meta-tests that currently assert that support-owned boundary.
- Keep `benchmark_test_support.py` focused on genuinely shared selectors, manifest helpers, signature helpers, runtime primitives, and anchor-contract utilities; make the combined source-tree suite own its remaining compiled-pattern contract payload/runtime/build-call helpers locally.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move or delete the remaining owner-only compiled-pattern contract helper surface from `tests/benchmarks/benchmark_test_support.py`, including:
  - `compiled_pattern_contract_expected_build_calls(...)`
  - `_run_cpython_compiled_pattern_module_helper_workload(...)`
  - `_assert_wrong_text_model_payload_round_trip(...)`
  - `_assert_compiled_pattern_module_success_payload_round_trip(...)`
  - `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`
  - `include_live_compiled_pattern_module_success_workload(...)`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it owns the moved compiled-pattern contract helper layer directly instead of reaching through `benchmark_test_support` for those names.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the tighter boundary:
  - `benchmark_test_support.py` no longer exports the moved compiled-pattern contract helper names
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved helpers locally
  - the surviving shared compiled-pattern selector/signature/runtime primitives that still have multiple consumers remain support-owned
- Keep the run bounded to this ownership cleanup:
  - do not move broader shared selector/signature helpers that still have multiple consumers across benchmark suites
  - do not change benchmark workloads, `python/rebar_harness/benchmarks.py`, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_contract_expected_build_calls or benchmark_test_support_owns_compiled_pattern_helper_surface or source_tree_combined_suite_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports or run_cpython_compiled_pattern_module_helper_workload or source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def compiled_pattern_contract_expected_build_calls\\(|^def _run_cpython_compiled_pattern_module_helper_workload\\(|^def _assert_wrong_text_model_payload_round_trip\\(|^def _assert_compiled_pattern_module_success_payload_round_trip\\(|^def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(|^def include_live_compiled_pattern_module_success_workload\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, and `.rebar/runtime/dashboard.md` already pointed at `HEAD` `eb2469ae3d04dfb1e3d12dfbe1e7e5255ba16229`, so the runtime counts were not lagging a dirty or older checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1428|RBR-1429|RBR-1430|RBR-1431" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1428` was available.
- Candidate selection in this run:
  - First candidate probe was not viable: `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns `_source_tree_contract_manifest(...)` and `_source_tree_contract_workload(...)`, and `tests/benchmarks/test_benchmark_test_support.py` already asserts those helpers are absent from `tests/benchmarks/benchmark_test_support.py`.
  - Second candidate probe stayed bounded: `rg -n "compiled_pattern_contract_expected_build_calls|_run_cpython_compiled_pattern_module_helper_workload|_assert_wrong_text_model_payload_round_trip|_assert_compiled_pattern_module_success_payload_round_trip|_assert_compiled_pattern_success_rows_measured_in_combined_manifest|include_live_compiled_pattern_module_success_workload" tests/benchmarks -g '*.py'` showed the remaining compiled-pattern contract helper layer still lives in `tests/benchmarks/benchmark_test_support.py`, with non-definition references limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus `tests/benchmarks/test_benchmark_test_support.py`.
  - `bash -lc "rg -n '^def compiled_pattern_contract_expected_build_calls\\(|^def _run_cpython_compiled_pattern_module_helper_workload\\(|^def _assert_wrong_text_model_payload_round_trip\\(|^def _assert_compiled_pattern_module_success_payload_round_trip\\(|^def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(|^def include_live_compiled_pattern_module_success_workload\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact support-owned helper layer this task deletes or localizes.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_contract_expected_build_calls or benchmark_test_support_owns_compiled_pattern_helper_surface or source_tree_combined_suite_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports or run_cpython_compiled_pattern_module_helper_workload or source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'` passed with `9 passed, 481 deselected in 0.29s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.

## Completion Note
- Moved the remaining compiled-pattern contract helper layer into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rewired that suite to call its local helpers directly.
- Removed the six owner-only helper definitions from `tests/benchmarks/benchmark_test_support.py` so shared support now only keeps the still-shared compiled-pattern selectors, signatures, and runtime primitives.
- Tightened `tests/benchmarks/test_benchmark_test_support.py` to assert the moved helper names are absent from shared support and present in the source-tree combined owner suite.
- Verification in this implementation run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_contract_expected_build_calls or benchmark_test_support_owns_compiled_pattern_helper_surface or source_tree_combined_suite_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports or run_cpython_compiled_pattern_module_helper_workload or source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers'` passed with `9 passed, 481 deselected in 0.62s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n '^def compiled_pattern_contract_expected_build_calls\\(|^def _run_cpython_compiled_pattern_module_helper_workload\\(|^def _assert_wrong_text_model_payload_round_trip\\(|^def _assert_compiled_pattern_module_success_payload_round_trip\\(|^def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(|^def include_live_compiled_pattern_module_success_workload\\(' tests/benchmarks/benchmark_test_support.py"` passed.
