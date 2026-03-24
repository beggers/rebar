# RBR-1210: Move benchmark summary contract tests onto publication runtime suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining generic benchmark scorecard-summary contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing publication/runtime owner in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the giant combined benchmark suite stops owning tests that only exercise `rebar_harness.benchmarks` summary-building helpers.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it becomes the owner for the current generic benchmark summary contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing helpers and tests into that dedicated file without widening their scope or changing their assertions:
  - `_summary_contract_workload_payload`
  - `_summary_contract_workload_record`
  - `_summary_contract_manifest`
  - `test_build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note`
  - `test_build_family_summary_marks_absent_module_family_and_keeps_deferred_note`
  - `test_build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap`
  - `test_build_manifest_summaries_marks_empty_module_boundary_selection_absent`
  - `test_build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current parser-versus-module family mix, cache-mode splits, readiness labels, and median timing expectations asserted by the three `build_family_summary(...)` tests;
  - preserve the current manifest-path, smoke-workload, `spec_refs`, and notes behavior asserted by the two `build_manifest_summaries(...)` tests;
  - keep using ordinary `BenchmarkManifest` and `workload_from_payload(...)` objects rather than inventing a new test-only representation; and
  - keep the current test names and assertion surfaces unchanged apart from relocating them.
- Reuse the existing publication/runtime suite instead of adding another test layer:
  - keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` as the dedicated owner for these generic scorecard/publication helper contracts;
  - do not add a new `*_support.py` module or another one-off contract suite for this extraction; and
  - do not widen this cleanup into selector, built-native, manifest-validation, or source-tree combined benchmark behavior beyond the named block above.
- Delete the moved helper/test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note or build_family_summary_marks_absent_module_family_and_keeps_deferred_note or build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap or build_manifest_summaries_marks_empty_module_boundary_selection_absent or build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only'`
- `bash -lc "! rg -n 'def _summary_contract_workload_payload\\(|def _summary_contract_workload_record\\(|def _summary_contract_manifest\\(|test_build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note|test_build_family_summary_marks_absent_module_family_and_keeps_deferred_note|test_build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap|test_build_manifest_summaries_marks_empty_module_boundary_selection_absent|test_build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1210` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1210|RBR-1211|RBR-1212|RBR-1213|RBR-1214" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed `RBR-1208` and `RBR-1209` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `15880` lines in this run;
  - `rg -n 'def _summary_contract_workload_payload\\(|def _summary_contract_workload_record\\(|def _summary_contract_manifest\\(|test_build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note|test_build_family_summary_marks_absent_module_family_and_keeps_deferred_note|test_build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap|test_build_manifest_summaries_marks_empty_module_boundary_selection_absent|test_build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` currently matches only the combined suite block at lines `10768`, `10812`, `10848`, `10880`, `10944`, `10989`, `11021`, and `11052`; and
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` already exists as the dedicated owner for generic benchmark publication/runtime contracts, so this cleanup removes one misplaced block instead of creating a sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py` returned `17 passed, 3 skipped in 0.13s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note or build_family_summary_marks_absent_module_family_and_keeps_deferred_note or build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap or build_manifest_summaries_marks_empty_module_boundary_selection_absent or build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only'` returned `5 passed, 447 deselected in 0.15s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the helper/test block still lives in the combined suite.
