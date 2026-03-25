## RBR-1304: Move conditional callable slice broker onto source-tree anchor support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining conditional-callable slice broker layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, so the combined benchmark suite stops owning both the assertions and the reusable workload-selection / slice-expectation support those assertions share.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it owns the conditional-callable slice helper surface that currently lives inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including these functions:
  - `_conditional_group_exists_callable_str_slice_workloads`
  - `_conditional_group_exists_callable_bytes_slice_workloads`
  - `_conditional_group_exists_quantified_callable_str_workloads`
  - `_conditional_group_exists_nested_callable_str_workloads`
  - `_conditional_group_exists_nested_callable_bytes_workloads`
  - `_conditional_group_exists_quantified_callable_bytes_workloads`
  - `_conditional_group_exists_alternation_callable_bytes_workloads`
  - `_split_workload_ids_by_text_model`
  - `_selected_workload_ids`
  - `_mirrored_bytes_workload_ids`
  - `_conditional_group_exists_template_replacement_expectation`
  - `_conditional_group_exists_callable_replacement_expectations`
  - `_conditional_group_exists_alternation_callable_replacement_expectation`
  - `_conditional_group_exists_nested_callable_replacement_expectation`
  - `_conditional_group_exists_nested_callable_bytes_replacement_expectation`
  - `_conditional_group_exists_quantified_callable_replacement_expectation`
  - `_conditional_group_exists_quantified_callable_bytes_replacement_expectation`
- Move any small import or helper dependency those functions need onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` while preserving the current slice semantics:
  - keep the current `"conditional-group-exists-boundary"` slice-id lookups and drift checks intact;
  - preserve the existing workload-id partitioning for `str` versus `bytes`;
  - preserve the current representative-workload selection behavior for negative-count, none-count, plain no-match, nested, quantified, alternation-heavy, and template replacement follow-ons; and
  - keep the helper API directly importable from `tests.benchmarks.source_tree_benchmark_anchor_support` without introducing a new broker module or compatibility wrapper.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved helper surface from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of defining it locally. After the cleanup, that suite should keep only the benchmark assertions and test-local class methods that are still specific to the combined suite.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it pins the slimmer ownership boundary directly:
  - assert the moved conditional-callable helper names are exposed from `tests.benchmarks.source_tree_benchmark_anchor_support`;
  - assert `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines those top-level helpers locally; and
  - keep the existing source-tree anchor-support assertions green.
- Do not move the two unittest classes or their assertion methods in this task. The target is the top-level conditional-callable broker surface above those classes, not a broader rewrite of the combined suite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'conditional_group_exists or source_tree_support_module_exposes_moved or combined_suite_no_longer_defines_moved'`
- `bash -lc "! rg -n '^def (_conditional_group_exists_callable_str_slice_workloads|_conditional_group_exists_callable_bytes_slice_workloads|_conditional_group_exists_quantified_callable_str_workloads|_conditional_group_exists_nested_callable_str_workloads|_conditional_group_exists_nested_callable_bytes_workloads|_conditional_group_exists_quantified_callable_bytes_workloads|_conditional_group_exists_alternation_callable_bytes_workloads|_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids|_conditional_group_exists_template_replacement_expectation|_conditional_group_exists_callable_replacement_expectations|_conditional_group_exists_alternation_callable_replacement_expectation|_conditional_group_exists_nested_callable_replacement_expectation|_conditional_group_exists_nested_callable_bytes_replacement_expectation|_conditional_group_exists_quantified_callable_replacement_expectation|_conditional_group_exists_quantified_callable_bytes_replacement_expectation)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the three files above. Do not widen it into benchmark workload manifests, harness runtime behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Do not add another support/broker module. Reuse `tests/benchmarks/source_tree_benchmark_anchor_support.py` as the owner for this helper surface.
- Preserve the current callable-replacement workload ids, slice ids, representative-workload expectations, and combined-suite benchmark assertions.

## Notes
- `RBR-1304` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1304|RBR-1305|RBR-1306" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1304`.
- No blocked architecture task existed to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, and no blocked tasks;
  - the most recent `architecture-implementation` run finished `done`; and
  - the only current runtime anomaly is a `reporting` timeout, not inherited-dirty queue churn or a task-commit refresh failure.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines the seventeen helper functions listed above locally at lines `142` through `336`;
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` currently has no definitions for those helper names; and
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` currently has no ownership assertions for this conditional-callable helper surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'conditional_group_exists or source_tree_support_module_exposes_moved or combined_suite_no_longer_defines_moved'` passed with `28 passed, 99 deselected, 812 subtests passed in 2.77s`;
  - `rg -n '^def (_conditional_group_exists_callable_str_slice_workloads|_conditional_group_exists_callable_bytes_slice_workloads|_conditional_group_exists_quantified_callable_str_workloads|_conditional_group_exists_nested_callable_str_workloads|_conditional_group_exists_nested_callable_bytes_workloads|_conditional_group_exists_quantified_callable_bytes_workloads|_conditional_group_exists_alternation_callable_bytes_workloads|_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids|_conditional_group_exists_template_replacement_expectation|_conditional_group_exists_callable_replacement_expectations|_conditional_group_exists_alternation_callable_replacement_expectation|_conditional_group_exists_nested_callable_replacement_expectation|_conditional_group_exists_nested_callable_bytes_replacement_expectation|_conditional_group_exists_quantified_callable_replacement_expectation|_conditional_group_exists_quantified_callable_bytes_replacement_expectation)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports all seventeen local definitions, and that failure belongs exactly to this cleanup; and
  - `rg -n 'conditional_group_exists_callable_str_slice_workloads|conditional_group_exists_callable_replacement_expectations|_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` currently returns no matches, confirming the owner/support coverage is still missing.
