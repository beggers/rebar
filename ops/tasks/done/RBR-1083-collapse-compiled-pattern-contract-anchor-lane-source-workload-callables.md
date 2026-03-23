## RBR-1083: Collapse compiled-pattern contract anchor-lane source-workload callables

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining callable-backed source-workload wrapper layer in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` for `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` so the anchored manifest checks read directly from concrete workload tuples instead of carrying `tuple | Callable[[], tuple]` plus a one-purpose normalizer helper.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these callable-normalization surfaces:
  - `_CompiledPatternModuleContractAnchorLane.source_workloads: tuple[Workload, ...] | Callable[[], tuple[Workload, ...]]`
  - `_compiled_pattern_module_contract_anchor_lane_source_workloads(...)`
- `_CompiledPatternModuleContractAnchorLane.source_workloads` stores concrete workload tuples only, and `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases` reads those tuples directly when building the temporary manifest.
- `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` no longer wires compile-contract lanes through `source_workloads=contract_case.source_workloads`; instead it materializes the exact current source workload tuples at lane construction time, or through a strictly smaller same-file equivalent that removes the callable-vs-tuple branch entirely.
- Keep the current anchored ownership surface intact after the cleanup:
  - the success-anchor lanes still use the exact workload tuples already carried by `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS`;
  - the compile-success and compile-keyword lanes still preserve the exact ordered source workload ids from `contract_case.expected_source_workload_ids()`;
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases` still covers both `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` through `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`; and
  - the existing compile-contract manifest, probe, callback, and anchor-pair assertions continue to cover the same contract filenames, workload ids, expected exceptions, and published correctness pairings.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n 'source_workloads: tuple\\[Workload, \\.\\.\\.\\] \\| Callable\\[\\[\\], tuple\\[Workload, \\.\\.\\.\\]\\]|def _compiled_pattern_module_contract_anchor_lane_source_workloads\\(|source_workloads=contract_case.source_workloads' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the callable-backed lane wrapper over introducing another helper family, registry object, or detached anchor abstraction.
- Keep the existing workload ids, ordering, contract filenames, anchor-pair expectations, callback behavior, and compile keyword/exception coverage intact.
- Reuse the already-materialized workload tuples as the ownership surface; do not reintroduce lazy wrappers around those same tuples under a different name.

## Notes
- `RBR-1083` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1082`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1083` task file; and
  - `rg -n 'RBR-1083|RBR-1084|RBR-1085|RBR-1086' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'source_workloads: tuple\\[Workload, \\.\\.\\.\\] \\| Callable\\[\\[\\], tuple\\[Workload, \\.\\.\\.\\]\\]|def _compiled_pattern_module_contract_anchor_lane_source_workloads\\(|source_workloads=contract_case.source_workloads' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the union-typed lane field at line `17206`, the one-purpose normalizer helper at lines `17218-17222`, and the remaining compile-contract callable assignment at line `17249` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` returned `64 passed, 662 deselected` in this run.

## Completion
- 2026-03-23: `_CompiledPatternModuleContractAnchorLane.source_workloads` now stores concrete workload tuples only, the one-purpose callable normalizer helper is deleted, the compile-contract anchor lanes materialize their tuple payloads eagerly at lane construction time, and the anchored-manifest assertion reads those tuples directly.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` returned `64 passed, 662 deselected`.
  - `bash -lc "! rg -n 'source_workloads: tuple\\[Workload, \\.\\.\\.\\] \\| Callable\\[\\[\\], tuple\\[Workload, \\.\\.\\.\\]\\]|def _compiled_pattern_module_contract_anchor_lane_source_workloads\\(|source_workloads=contract_case.source_workloads' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` returned success with no matches.
