## RBR-1085: Retire dead benchmark loader-contract main block

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the unreachable `if __name__ == "__main__": unittest.main()` block and its dead duplicate callable-loader assertions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the benchmark-owner suite has one live pytest-owned loader-contract surface instead of one real test plus one dead copy.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer contains a repo-local `if __name__ == "__main__":` entry point or a nested `unittest.main()` call.
- The dead duplicate `python-benchmark-loader-contract` assertion block that currently sits under that `__main__` guard is deleted, leaving `test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(...)` as the only loader-contract assertion surface in the file.
- Keep the live synthetic-manifest benchmark contract coverage intact after the cleanup:
  - `test_standard_benchmark_manifest_materializes_callable_replacement_descriptors`
  - `test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order`
  - `test_standard_benchmark_manifest_measures_expected_exception_workloads`
  - `test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable`
  - `test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads`
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_materializes_callable_replacement_descriptors or standard_benchmark_manifest_selected_workloads_preserves_filters_and_order or standard_benchmark_manifest_measures_expected_exception_workloads or run_internal_workload_probe_reports_unsupported_operations_as_unavailable or standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads'`
- `bash -lc "! rg -n '^if __name__ == \"__main__\":|^\\s+unittest\\.main\\(\\)$' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the dead block over moving it behind another wrapper, sentinel, or helper.
- Keep the live pytest test names, synthetic manifest payloads, workload ids, and current assertion coverage intact.
- Do not replace the deleted dead block with another script-style execution path in this file.

## Notes
- `RBR-1085` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1084`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1085` task file; and
  - `rg -n 'RBR-1085|RBR-1086|RBR-1087|RBR-1088' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only the historical mention inside `ops/tasks/done/RBR-1083-collapse-compiled-pattern-contract-anchor-lane-source-workload-callables.md`, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The structural drift is concrete in the live checkout:
  - `rg -n '__main__|unittest\\.main\\(|python-benchmark-loader-contract' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the live test copy around lines `11242-11388`, the dead `if __name__ == "__main__":` / `unittest.main()` block at lines `20121-20122`, and the duplicated loader-contract assertions immediately below that block in this run.
- The focused synthetic-manifest verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_materializes_callable_replacement_descriptors or standard_benchmark_manifest_selected_workloads_preserves_filters_and_order or standard_benchmark_manifest_measures_expected_exception_workloads or run_internal_workload_probe_reports_unsupported_operations_as_unavailable or standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads'` returned `6 passed, 720 deselected` in this run.
