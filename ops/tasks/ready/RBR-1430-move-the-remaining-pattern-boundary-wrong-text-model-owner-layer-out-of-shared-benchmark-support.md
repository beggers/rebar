## RBR-1430: Move the remaining pattern-boundary wrong-text-model owner layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining pattern-boundary wrong-text-model owner-only helper layer from `tests/benchmarks/benchmark_test_support.py`.
- Shared benchmark support still owns the pattern-boundary wrong-text-model manifest constant, source-workload selector, callback-call expectation helper, correctness/workload signature helpers, and workload selector even though the only live consumer path is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the meta-tests that currently assert that support-owned boundary.
- Keep `benchmark_test_support.py` focused on genuinely shared manifest helpers, runtime probes, generic signature utilities, and multi-suite benchmark selectors; make the source-tree combined suite own its remaining pattern-boundary wrong-text-model lane directly.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move or delete the remaining pattern-boundary wrong-text-model owner-only helper surface from `tests/benchmarks/benchmark_test_support.py`, including:
  - `PATTERN_BOUNDARY_MANIFEST_PATH`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_pattern_boundary_wrong_text_model_source_workloads(...)`
  - `_pattern_boundary_wrong_text_model_expected_callback_call(...)`
  - `_pattern_boundary_wrong_text_model_correctness_case_signature(...)`
  - `_pattern_boundary_wrong_text_model_workload_signature(...)`
  - `_is_pattern_boundary_wrong_text_model_workload(...)`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so its pattern-boundary standard-definition block and its haystack-text-model contract coverage call the moved local manifest/selector/signature helpers directly instead of reaching through `benchmark_test_support` for those names.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the tighter boundary:
  - `benchmark_test_support.py` no longer exports the moved pattern-boundary wrong-text-model helper names
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved manifest/selector/signature helpers locally
  - the surviving pattern-boundary helpers that still have multiple consumers remain support-owned
- Keep the run bounded to this ownership cleanup:
  - do not move other shared pattern-boundary helpers that still serve multiple suites
  - do not change benchmark workloads, `python/rebar_harness/benchmarks.py`, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_wrong_text_model or wrong_text_model_payload_round_trip or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or source_tree_combined_suite_owns_rehomed_pattern_boundary_wrong_text_model_surface_locally or benchmark_test_support_owns_pattern_boundary_wrong_text_model_surface'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def _pattern_boundary_wrong_text_model_source_workloads\\(|^def _pattern_boundary_wrong_text_model_expected_callback_call\\(|^def _pattern_boundary_wrong_text_model_correctness_case_signature\\(|^def _pattern_boundary_wrong_text_model_workload_signature\\(|^def _is_pattern_boundary_wrong_text_model_workload\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, and `.rebar/runtime/dashboard.md` already pointed at `HEAD` `d831f1c691fa4ac1fe6507683ea7afbc22d6b44e`, so the runtime counts were not lagging a dirty or older checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1430|RBR-1431|RBR-1432|RBR-1433" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1430` was available.
- Candidate selection in this run:
  - `rg -n "_pattern_boundary_wrong_text_model_source_workloads|_pattern_boundary_wrong_text_model_expected_callback_call|_pattern_boundary_wrong_text_model_correctness_case_signature|_pattern_boundary_wrong_text_model_workload_signature|_is_pattern_boundary_wrong_text_model_workload" tests/benchmarks -g '*.py'` showed the entire pattern-boundary wrong-text-model lane still lives in `tests/benchmarks/benchmark_test_support.py`, with non-definition references limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the meta-tests that currently assert that support-owned boundary.
  - The source-tree combined suite still routes both its `StandardBenchmarkAnchorContractDefinition(name="pattern-boundary-wrong-text-model", ...)` block and its `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(...)` coverage through support-owned manifest/selector/signature helpers.
  - A second candidate also existed, `_artifact_manifest_record(...)` plus `_assert_benchmark_summary_consistent(...)`, but this task keeps the run smaller by taking the already-cohesive pattern-boundary wrong-text-model selector/signature lane first.
  - `bash -lc "rg -n '^def _pattern_boundary_wrong_text_model_source_workloads\\(|^def _pattern_boundary_wrong_text_model_expected_callback_call\\(|^def _pattern_boundary_wrong_text_model_correctness_case_signature\\(|^def _pattern_boundary_wrong_text_model_workload_signature\\(|^def _is_pattern_boundary_wrong_text_model_workload\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact support-owned helper layer this task deletes or localizes.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_wrong_text_model or wrong_text_model_payload_round_trip or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or source_tree_combined_suite_owns_rehomed_pattern_boundary_wrong_text_model_surface_locally or benchmark_test_support_owns_pattern_boundary_wrong_text_model_surface'` passed with `3 passed, 493 deselected in 0.22s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
