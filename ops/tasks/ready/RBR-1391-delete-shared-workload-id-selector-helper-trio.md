## RBR-1391: Delete the shared workload-id selector helper trio

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the tiny shared workload-id selector layer that still lives in `tests/benchmarks/benchmark_test_support.py` only to support the source-tree owner suites. The remaining helper trio is not benchmark-support-specific anymore; it is just partition/filter glue for two source-tree benchmark test files and should be deleted instead of kept as another shared wrapper surface.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete these helper functions from `tests/benchmarks/benchmark_test_support.py` instead of moving or renaming them:
  - `_split_workload_ids_by_text_model(...)`
  - `_selected_workload_ids(...)`
  - `_mirrored_bytes_workload_ids(...)`
- Rewrite the remaining call sites in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so they use direct tuple comprehensions or other already-local selection logic, without introducing another replacement wrapper layer in either file.
- Keep the cleanup bounded to this selector-helper deletion. Do not widen into unrelated benchmark-support churn, source-tree scorecard refactors, or collection-replacement support moves.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, generated reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'moved_conditional_callable_selector_helpers_keep_partition_rules or moved_conditional_callable_workload_loaders_pin_expected_ids'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_callable_scorecards_keep_none_count_follow_on_workloads_in_sync or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync'`
- `bash -lc '! rg -n "(def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b|benchmark_test_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b)" tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py'`

## Constraints
- Prefer deleting the helper layer outright over rehoming it to another support module or replacing it with another indirection under `tests/benchmarks/`.
- If one assertion block still wants a local helper after the rewrite, keep it file-local to the owning test file and scoped only to that test block; do not recreate a cross-file support surface.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1391|RBR-1392|RBR-1393' ops/state/backlog.md ops/state/current_status.md` returned no reserved future-id hits for `RBR-1391`.
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this checkout, so there was no ready or blocked duplicate to refine or reopen first.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - With tracked and live JSON counts both at zero, I looked for one remaining cross-file helper layer rather than another local naming cleanup.
  - `rg -n "_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids" tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the trio now exists only as definitions in `tests/benchmarks/benchmark_test_support.py` and as call sites in the two source-tree owner suites.
  - That leaves benchmark support carrying three generic tuple/filter wrappers for only two owner-local consumers, which is a better bounded post-JSON simplification target than another single-file support cleanup.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'moved_conditional_callable_selector_helpers_keep_partition_rules or moved_conditional_callable_workload_loaders_pin_expected_ids'` passed with `2 passed, 114 deselected in 0.13s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync or conditional_group_exists_callable_scorecards_keep_none_count_follow_on_workloads_in_sync or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync'` passed with `3 passed, 276 deselected in 0.16s`.
  - `bash -lc 'rg -n "(def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b|benchmark_test_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b)" tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py'` currently reports the exact helper definitions and call sites this task is intended to delete.
