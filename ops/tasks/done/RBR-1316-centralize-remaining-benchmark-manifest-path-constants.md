# RBR-1316: Centralize source-tree benchmark manifest path constants

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the duplicated source-tree benchmark workload-path constant layer so `tests/benchmarks/source_tree_benchmark_anchor_support.py` reuses one shared owner in `tests/benchmarks/benchmark_test_support.py` instead of hard-coding overlapping `*_MANIFEST_PATH` assignments locally.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add shared benchmark-manifest path constants to `tests/benchmarks/benchmark_test_support.py` for the remaining source-tree workload files that are still assigned locally in `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `optional_group_boundary.py`
  - `nested_group_boundary.py`
  - `exact_repeat_quantified_group_boundary.py`
  - `ranged_repeat_quantified_group_boundary.py`
  - `grouped_alternation_boundary.py`
  - `grouped_alternation_replacement_boundary.py`
  - `nested_group_replacement_boundary.py`
  - `open_ended_quantified_group_boundary.py`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to import and reuse those shared constants instead of assigning its own local `*_MANIFEST_PATH` values.
- Keep the owner boundary explicit in the contract suites:
  - update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so its manifest-path ownership assertions now prove the source-tree support module reuses the shared support constants by identity and no longer defines its own copies
  - update `tests/benchmarks/test_benchmark_test_support.py` so the shared-owner contract covers the moved source-tree constants alongside the existing `MODULE_BOUNDARY_MANIFEST_PATH` checks
- Do not add a new helper module, alias table, or compatibility wrapper. Reuse the existing owner module `tests/benchmarks/benchmark_test_support.py`.
- Keep this cleanup structural:
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, README text, or tracked `ops/state/` prose
  - do not broaden the task into publication-runtime alias cleanup, source-tree expectation rewrites, or benchmark-slice behavior changes

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant or inline_standard_definition_exports_reuse_named_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_owner_builders_reference_owner_manifest_path_constants or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants'`
- `bash -lc "! rg -n '^(OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH) =' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

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
  - `.rebar/runtime/dashboard.md` reports a clean worktree, `1` ready architecture task, `0` blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows a requeued timeout on this same architecture task, but no inherited-dirty, refresh, or commit anomaly that would trigger the rule-10 no-op path
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines eight local benchmark workload-path constants that overlap the shared support layer
  - `tests/benchmarks/benchmark_test_support.py` already owns adjacent benchmark manifest constants such as `COMPILE_MATRIX_MANIFEST_PATH`, `REGRESSION_MATRIX_MANIFEST_PATH`, `MODULE_BOUNDARY_MANIFEST_PATH`, `COLLECTION_REPLACEMENT_MANIFEST_PATH`, and `PATTERN_BOUNDARY_MANIFEST_PATH`, so the remaining source-tree literals are drift rather than a distinct ownership pattern
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still has its own two local manifest-path aliases, but that independent cleanup is out of scope for this narrowed run
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant or inline_standard_definition_exports_reuse_named_manifest_path_constants'` passed with `5 passed, 91 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_owner_builders_reference_owner_manifest_path_constants or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants'` passed with `3 passed, 47 deselected in 0.11s`
  - `bash -lc "! rg -n '^(OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH) =' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those duplicated local constant assignments still exist, and that failure belongs exactly to this cleanup.
- 2026-03-25T15:47:27+00:00: harness requeued after failed or incomplete run after run `20260325T150727Z-architecture-implementation-RBR-1316-centralize-remaining-benchmark-manifest-path-constants` (exit=124, timed_out=true).
- 2026-03-25T16:08:00+00:00: task narrowed after the timeout so the next implementation pass only has to centralize the source-tree support constants; leave the two publication-runtime aliases for a separate follow-on cleanup if they still remain afterward.
- 2026-03-25T16:32:00+00:00: landed by moving the eight remaining source-tree manifest path constants into `tests/benchmarks/benchmark_test_support.py`, switching `tests/benchmarks/source_tree_benchmark_anchor_support.py` to import and reuse them, and updating both benchmark contract suites to assert identity plus imported-not-assigned ownership.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant or inline_standard_definition_exports_reuse_named_manifest_path_constants'` -> `5 passed, 100 deselected in 0.17s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_manifest_path_constants_point_to_current_workload_files or source_tree_owner_builders_reference_owner_manifest_path_constants or source_tree_owner_definition_exports_reuse_owner_manifest_path_constants'` -> `3 passed, 47 deselected in 0.17s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_manifest_path_consumers_reuse_support_constants_by_identity or shared_source_tree_manifest_path_constants_point_to_current_workload_files'` -> `9 passed, 96 deselected in 0.11s`
  - `bash -lc "! rg -n '^(OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH) =' tests/benchmarks/source_tree_benchmark_anchor_support.py"` -> passed
