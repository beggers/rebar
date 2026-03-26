## RBR-1429: Move the remaining source-tree combined correctness-anchor signature layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-combined-only correctness-anchor signature/filter layer from `tests/benchmarks/benchmark_test_support.py`.
- After `RBR-1428`, shared benchmark support still owns the optional-group, nested-group, counted-repeat, and grouped-alternation correctness-anchor selector/signature helpers even though the only live consumer is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Keep `benchmark_test_support.py` focused on genuinely shared runtime primitives, manifest helpers, generic signature-freezing utilities, and anchor-contract helpers; make the source-tree combined suite own its remaining correctness-anchor selector/signature layer directly.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move or delete the remaining source-tree-combined-only correctness-anchor selector/signature helper surface from `tests/benchmarks/benchmark_test_support.py`, including:
  - `_optional_group_correctness_case_signature(...)`
  - `_optional_group_workload_signature(...)`
  - `_is_optional_group_conditional_workload(...)`
  - `_nested_group_correctness_case_signature(...)`
  - `_nested_group_workload_signature(...)`
  - `_counted_repeat_correctness_case_signature(...)`
  - `_counted_repeat_workload_signature(...)`
  - `_is_non_alternation_counted_repeat_workload(...)`
  - `_grouped_alternation_correctness_case_signature(...)`
  - `_grouped_alternation_workload_signature(...)`
  - `_grouped_alternation_replacement_correctness_case_signature(...)`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so its `StandardBenchmarkAnchorContractDefinition(...)` blocks and any related owner helpers call the moved local selector/signature functions directly instead of reaching through `benchmark_test_support` for those names.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the tighter boundary:
  - `benchmark_test_support.py` no longer exports the moved source-tree combined correctness-anchor helper names
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved selector/signature helper names locally
  - the surviving generic helpers that still have multiple consumers, including `freeze_signature_value(...)`, remain support-owned
- Keep the run bounded to this ownership cleanup:
  - do not move generic helpers that are still shared across benchmark modules
  - do not change benchmark workloads, `python/rebar_harness/benchmarks.py`, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'optional_group or nested_group or counted_repeat or grouped_alternation or source_tree_combined_suite_owns_rehomed_manifest_expectation_surface_locally'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def _optional_group_correctness_case_signature\\(|^def _optional_group_workload_signature\\(|^def _is_optional_group_conditional_workload\\(|^def _nested_group_correctness_case_signature\\(|^def _nested_group_workload_signature\\(|^def _counted_repeat_correctness_case_signature\\(|^def _counted_repeat_workload_signature\\(|^def _is_non_alternation_counted_repeat_workload\\(|^def _grouped_alternation_correctness_case_signature\\(|^def _grouped_alternation_workload_signature\\(|^def _grouped_alternation_replacement_correctness_case_signature\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, and `.rebar/runtime/dashboard.md` already pointed at `HEAD` `b62b5882de6701f8c115afb45c5db07b12e0713c`, so the runtime counts were not lagging a dirty or older checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1429|RBR-1430|RBR-1431|RBR-1432" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1429` was available.
- Candidate selection in this run:
  - `rg -n "_optional_group_correctness_case_signature|_optional_group_workload_signature|_is_optional_group_conditional_workload|_nested_group_correctness_case_signature|_nested_group_workload_signature|_counted_repeat_correctness_case_signature|_counted_repeat_workload_signature|_is_non_alternation_counted_repeat_workload|_grouped_alternation_correctness_case_signature|_grouped_alternation_workload_signature|_grouped_alternation_replacement_correctness_case_signature" tests/benchmarks -g '*.py'` showed those helpers are defined only in `tests/benchmarks/benchmark_test_support.py` and referenced only from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - A follow-up file-by-file check confirmed there are no non-self references to those names from any other benchmark module, so this is still a source-tree-combined owner layer rather than a genuinely shared support surface.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently routes the `optional-group-conditional`, `nested-group`, `exact-repeat`, `ranged-repeat`, `grouped-alternation`, and grouped-alternation replacement anchor definitions through `benchmark_test_support` for that helper set.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'optional_group or nested_group or counted_repeat or grouped_alternation or source_tree_combined_suite_owns_rehomed_manifest_expectation_surface_locally'` passed with `33 passed, 459 deselected, 115 subtests passed in 1.93s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n '^def _optional_group_correctness_case_signature\\(|^def _optional_group_workload_signature\\(|^def _is_optional_group_conditional_workload\\(|^def _nested_group_correctness_case_signature\\(|^def _nested_group_workload_signature\\(|^def _counted_repeat_correctness_case_signature\\(|^def _counted_repeat_workload_signature\\(|^def _is_non_alternation_counted_repeat_workload\\(|^def _grouped_alternation_correctness_case_signature\\(|^def _grouped_alternation_workload_signature\\(|^def _grouped_alternation_replacement_correctness_case_signature\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact support-owned helper layer this task deletes or localizes.
