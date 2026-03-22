# RBR-0917: Collapse compiled-pattern module-boundary success manifest mirror

Status: done
Owner: cleanup
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the duplicated inline compiled-pattern module-boundary success manifest dict from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the neighboring owner tests build that manifest through one file-local helper instead of repeating the same `module-boundary` structure.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Notes
- The bounded target was concrete in the live checkout:
  - the owner file repeated the same `"schema_version": 1`, `"manifest_id": "module-boundary"`, and shared defaults block in both `test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_success_rows_until_helper_invocation()` and `test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases()`;
  - both tests already sourced workloads through `_compiled_pattern_module_boundary_success_manifest_payload(case)`, so collapsing the dict shape into one helper stayed file-local and structural only; and
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_boundary_success'` passed before the edit in this run.
- `RBR-0917` was unreserved in this checkout for a durable cleanup note:
  - `rg -n 'RBR-0917|RBR-0918|RBR-0919' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` found no existing task or reserved follow-on for `RBR-0917`.

## Completion
- Added `_compiled_pattern_module_boundary_success_manifest()` to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and routed the two compiled-pattern module-boundary success owner tests through it instead of rebuilding the same inline manifest dict twice.
- Verified with:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_boundary_success'`
