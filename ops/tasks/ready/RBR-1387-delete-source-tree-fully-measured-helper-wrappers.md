## RBR-1387: Delete source-tree fully measured helper wrappers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the two thin fully-measured helper wrappers from the shared source-tree benchmark owner layer, and have the affected combined benchmark assertions read directly from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` plus the stored `fully_measured_expectation` field instead of routing that data through helper functions.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove these helper functions from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without replacing them with another alias, registry, or helper layer:
  - `source_tree_combined_fully_measured_manifest_ids`
  - `source_tree_combined_fully_measured_manifest_expectation`
- Rewrite the affected assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so they keep the same behavior through direct reads of `source_tree_support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` and each manifest definition's existing `fully_measured_expectation` field:
  - coverage-group filtering must still preserve the current manifest-id ordering for the counted-repeat path;
  - the quantified-alternation and regression checks must still read the same representative workload ids plus measured/total workload counts;
  - preserve the current equality checks between manifest definitions, combined-case expectations, and the stored fully measured expectations.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the owner/test surface treats the deleted helpers as absent from the module while keeping the remaining shared support API and local-definition checks precise enough to catch regressions.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured or quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured or regression_manifest_is_fully_measured_on_the_shared_surface or combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(def source_tree_combined_fully_measured_manifest_(ids|expectation)\\()|source_tree_support\\.source_tree_combined_fully_measured_manifest_(ids|expectation)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer direct iteration of `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()` and direct reads of each manifest definition's `fully_measured_expectation` field over any new helper or owner-surface wrapper.
- Keep the run bounded to deleting these two wrappers and rewiring their current consumer checks; do not reopen the larger source-tree combined-case builder stack in the same task.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, so the runtime JSON count was not lagging a dirty checkout in this run.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1387|RBR-1388|RBR-1389|RBR-1390' ops/state/current_status.md ops/state/backlog.md` returned no reserved future id hits for `RBR-1387`.
  - `ops/tasks/ready/` and `ops/tasks/blocked/` were empty in this checkout, so there was no ready/blocked duplicate to refine or reopen first.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - The first candidate I inspected was the source-tree fully-measured owner surface because `source_tree_combined_fully_measured_manifest_ids(...)` and `source_tree_combined_fully_measured_manifest_expectation(...)` are thin wrappers over `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`.
  - Their live consumer surface is bounded to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and the support-module structure test already isolates the exported owner API in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`.
  - Direct reads of the manifest-definition dict already expose the same stored `fully_measured_expectation` objects and coverage-group metadata, so deleting the wrappers removes one more benchmark-support transit layer without touching runtime harness logic or benchmark publications.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `109 passed in 1.17s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured or quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured or regression_manifest_is_fully_measured_on_the_shared_surface or combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured'` passed with `3 passed, 276 deselected, 4 subtests passed in 0.43s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n '^(def source_tree_combined_fully_measured_manifest_(ids|expectation)\()|source_tree_support\.source_tree_combined_fully_measured_manifest_(ids|expectation)\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact wrapper definitions and test call sites this task is intended to delete.
