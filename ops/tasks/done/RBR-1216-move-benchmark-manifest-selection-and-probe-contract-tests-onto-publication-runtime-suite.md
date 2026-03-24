# RBR-1216: Move benchmark manifest selection and probe contract tests onto publication runtime suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining benchmark manifest-selection and internal workload-probe contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing publication/runtime owner in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the giant combined benchmark suite stops owning another generic harness-runtime surface.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it becomes the owner for the current manifest-selection and internal workload-probe contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order`
  - `test_standard_benchmark_manifest_measures_expected_exception_workloads`
  - `test_run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable`
  - `test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current manifest payloads, workload ids, selection ordering, smoke-selection filtering, missing-workload and unknown-selection-mode assertions, expected-exception payload round-trips, and unavailable-reason strings;
  - preserve the current `import_name` / `adapter_name` parametrization, the measured-status assertions for both `re` and `rebar`, and the current monkeypatched mismatch behavior for `run_internal_workload_probe(...)`;
  - preserve the current pytest parametrization ids and test names apart from relocating them; and
  - keep using ordinary `_write_test_manifest(...)`, `load_manifest(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` calls rather than inventing a new test-only representation.
- Reuse the existing dedicated suite instead of adding another architectural layer:
  - keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` as the owner for this benchmark runtime contract surface;
  - do not add a new `*_support.py` module or another one-off contract suite for this extraction; and
  - do not widen this cleanup into bytes-template replacement contracts, keyword-descriptor contracts, benchmark harness implementation code, or workload-manifest edits.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_selected_workloads_preserves_filters_and_order or standard_benchmark_manifest_measures_expected_exception_workloads or run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable or run_internal_workload_probe_reports_unsupported_operations_as_unavailable'`
- `bash -lc "! rg -n 'test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order|test_standard_benchmark_manifest_measures_expected_exception_workloads|test_run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable|test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1216` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run before this task was added; and
  - `rg -n "RBR-1216|RBR-1217|RBR-1218" ops/state/current_status.md ops/state/backlog.md` returned no matches, so this range was not reserved by planning-owned frontier notes.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains only `.gitkeep` in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed `RBR-1214` and `RBR-1215` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `rg -n 'def test_(standard_benchmark_manifest_selected_workloads_preserves_filters_and_order|standard_benchmark_manifest_measures_expected_exception_workloads|run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable|run_internal_workload_probe_reports_unsupported_operations_as_unavailable)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` currently matches only the combined-suite block at lines `12357`, `12439`, `12552`, and `12638`;
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` already exists as the dedicated owner for benchmark publication/runtime contracts; and
  - this task removes one misplaced harness-runtime block instead of creating a sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_selected_workloads_preserves_filters_and_order or standard_benchmark_manifest_measures_expected_exception_workloads or run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable or run_internal_workload_probe_reports_unsupported_operations_as_unavailable'` returned `7 passed, 374 deselected in 0.18s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those four tests still live in the combined suite.

## Completion
- Moved the four benchmark manifest-selection and internal workload-probe contract tests into `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` without changing their names, parametrization ids, helper usage, or assertion surfaces, and deleted the originals from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_selected_workloads_preserves_filters_and_order or standard_benchmark_manifest_measures_expected_exception_workloads or run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable or run_internal_workload_probe_reports_unsupported_operations_as_unavailable'` (`7 passed, 371 deselected in 0.33s`).
- Verified the old combined suite no longer owns those tests with `bash -lc "! rg -n 'test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order|test_standard_benchmark_manifest_measures_expected_exception_workloads|test_run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable|test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
