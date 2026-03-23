## RBR-1081: Collapse compiled-pattern success anchor source-workload callables

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining source-workload callable wrapper layer in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` for the compiled-pattern success anchor surface so the already-materialized success workload tuples flow directly into the success anchor specs and anchor-lane assembly instead of bouncing through `source_workloads=lambda owner_spec: ...` callables.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines the one-purpose success-anchor source-workload callable field on `_CompiledPatternModuleSuccessAnchorSpec`:
  - `source_workloads: Callable[[CompiledPatternModuleSuccessOwnerSpec], tuple[Workload, ...]]`
- `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` no longer wraps precomputed success workload tuples behind either of these one-purpose callable adapters:
  - `source_workloads=lambda owner_spec: owner_spec.source_workloads()`
  - `source_workloads=lambda owner_spec: _selected_manifest_workloads(...)`
- `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` no longer routes the success-anchor source workloads through `lambda anchor_spec=anchor_spec: anchor_spec.source_workloads(anchor_spec.owner_spec)` and instead reads directly from the success anchor specs or a strictly smaller same-file equivalent.
- Keep the current success-anchor ownership surface intact after the cleanup:
  - the `collection-replacement` success anchor still uses the exact ordered workload ids from `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC.expected_source_workload_ids`;
  - the `module-boundary-verbose-bytes` success anchor still uses the exact ordered workload ids selected from `MODULE_BOUNDARY_MANIFEST_PATH` by `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload`;
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases` still covers both `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` through `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`; and
  - the existing success manifest, probe, and precompile-first callback checks continue to cover the same anchored workload ids, callback arguments, and published correctness pairings.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n 'source_workloads: Callable\\[\\[CompiledPatternModuleSuccessOwnerSpec\\], tuple\\[Workload, \\.\\.\\.\\]\\]|source_workloads=lambda owner_spec|lambda anchor_spec=anchor_spec: anchor_spec.source_workloads\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the success-anchor callable wrapper layer over introducing another helper family, registry object, or detached support abstraction.
- Keep the current workload ids, ordering, contract filenames, anchored-case pairings, callback/probe behavior, and published correctness hooks intact.
- Reuse the already-materialized workload tuples as the ownership surface; do not reintroduce lazy wrappers around those same tuples under a different name.

## Notes
- `RBR-1081` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1080`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1081` task file; and
  - `rg -n 'RBR-1081|RBR-1082|RBR-1083' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'source_workloads: Callable\\[|source_workloads=lambda owner_spec|lambda anchor_spec=anchor_spec|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the success-anchor callable field at line `16389`, the two `source_workloads=lambda owner_spec: ...` adapters at lines `16418` and `16455`, and the `lambda anchor_spec=anchor_spec: anchor_spec.source_workloads(...)` wrapper at line `17221` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'` returned `50 passed, 676 deselected` in this run.

## Completion
- Landed a file-local cleanup in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` that replaces the success-anchor `source_workloads` callable field with concrete workload tuples, precomputes the collection-replacement and module-boundary verbose-bytes success anchor workload tuples after the shared workload selector helper is defined, and lets `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` read those tuples directly while still accepting callable-backed compile contract lanes.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'`
  - `bash -lc "! rg -n 'source_workloads: Callable\\[\\[CompiledPatternModuleSuccessOwnerSpec\\], tuple\\[Workload, \\.\\.\\.\\]\\]|source_workloads=lambda owner_spec|lambda anchor_spec=anchor_spec: anchor_spec.source_workloads\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
