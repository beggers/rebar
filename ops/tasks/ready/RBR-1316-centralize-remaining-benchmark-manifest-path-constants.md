# RBR-1316: Centralize remaining benchmark manifest path constants

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicated benchmark workload-path constant layer so `tests/benchmarks/source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` reuse one shared owner in `tests/benchmarks/benchmark_test_support.py` instead of hard-coding overlapping `*_MANIFEST_PATH` assignments locally.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`

## Acceptance Criteria
- Add shared benchmark-manifest path constants to `tests/benchmarks/benchmark_test_support.py` for the remaining workload files that are still assigned locally elsewhere in this benchmark-support surface:
  - `optional_group_boundary.py`
  - `nested_group_boundary.py`
  - `exact_repeat_quantified_group_boundary.py`
  - `ranged_repeat_quantified_group_boundary.py`
  - `grouped_alternation_boundary.py`
  - `grouped_alternation_replacement_boundary.py`
  - `nested_group_replacement_boundary.py`
  - `open_ended_quantified_group_boundary.py`
  - `conditional_group_exists_boundary.py`
  - `nested_group_callable_replacement_boundary.py`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to import and reuse those shared constants instead of assigning its own local `*_MANIFEST_PATH` values.
- Update `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` to import and reuse the shared conditional/callable-replacement manifest constants instead of keeping local aliases.
- Keep the owner boundary explicit in the contract suites:
  - update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so its manifest-path ownership assertions now prove the source-tree support module reuses the shared support constants by identity and no longer defines its own copies
  - update `tests/benchmarks/test_benchmark_test_support.py` with an AST-level or import-surface check that `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` imports the moved manifest constants from `tests.benchmarks.benchmark_test_support`
- Do not add a new helper module, alias table, or compatibility wrapper. Reuse the existing owner module `tests/benchmarks/benchmark_test_support.py`.
- Keep this cleanup structural:
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not broaden the task into source-tree expectation rewrites or benchmark-slice behavior changes

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant or inline_standard_definition_exports_reuse_named_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_owner_builders_reference_owner_manifest_path_constants or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads or conditional_group_exists_callable_none_count_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_workloads_round_trip_preserves_expected_exception_contract or run_internal_workload_probe_measures_conditional_group_exists_callable_none_count_workloads'`
- `bash -lc "! rg -n '^(OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH|_CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH|_NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH) =' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py"`

## Constraints
- Keep the cleanup bounded to shared manifest-path ownership across the benchmark support and benchmark contract test layers.
- Prefer deleting the duplicated local constant assignments over adding another indirection layer or renaming the owner surface again.

## Notes
- `RBR-1316` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1316|RBR-1317|RBR-1318' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1316*' -o -name 'RBR-1317*' -o -name 'RBR-1318*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`
  - the latest runtime dashboard showed no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines eight local benchmark workload-path constants that overlap the shared support layer
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still defines two more local manifest-path aliases for the same benchmark workload root
  - `tests/benchmarks/benchmark_test_support.py` already owns adjacent benchmark manifest constants such as `COMPILE_MATRIX_MANIFEST_PATH`, `REGRESSION_MATRIX_MANIFEST_PATH`, `MODULE_BOUNDARY_MANIFEST_PATH`, `COLLECTION_REPLACEMENT_MANIFEST_PATH`, and `PATTERN_BOUNDARY_MANIFEST_PATH`, so the remaining literals are drift rather than a distinct ownership pattern
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant or inline_standard_definition_exports_reuse_named_manifest_path_constants'` passed with `5 passed, 91 deselected in 0.17s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_owner_builders_reference_owner_manifest_path_constants or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants'` passed with `3 passed, 46 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results or run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads or conditional_group_exists_callable_none_count_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_workloads_round_trip_preserves_expected_exception_contract or run_internal_workload_probe_measures_conditional_group_exists_callable_none_count_workloads'` passed with `12 passed, 180 deselected in 0.13s`
  - `bash -lc "! rg -n '^(OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH|_CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH|_NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH) =' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py"` currently fails because those duplicated local constant assignments still exist, and that failure belongs exactly to this cleanup.
