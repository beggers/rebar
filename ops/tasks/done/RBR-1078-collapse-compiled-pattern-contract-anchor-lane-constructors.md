# RBR-1078: Collapse compiled-pattern contract anchor-lane constructors

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the last two thin compiled-pattern contract anchor-lane constructor helpers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared anchor-test lane is built directly from the existing contract carriers instead of bouncing through two one-purpose wrapper functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these thin anchor-lane constructor helpers:
  - `def _compiled_pattern_module_success_anchor_lane(...)`
  - `def _compiled_pattern_module_compile_contract_anchor_lane(...)`
- Replace that wrapper layer with direct use of the existing contract carriers, or a strictly smaller same-file equivalent:
  - `_CompiledPatternModuleSuccessAnchorSpec`
  - `CompiledPatternModuleCompileContractCase`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Keep the current shared anchor-lane semantics intact after the cleanup:
  - the success-anchor lanes still use `anchor_spec.case_id`, `anchor_spec.contract_filename`, `anchor_spec.expected_anchor_case_ids(...)`, `published_case_ids_by_signature(anchor_spec.correctness_case_signature)`, `anchor_spec.workload_signature`, `anchor_spec.include_workload`, and `anchor_spec.expected_anchored_pairs`;
  - the compile-contract lanes still use `contract_case.case_id`, `contract_case.anchor_contract_filename`, `contract_case.source_workloads`, `contract_case.contract_builder_spec`, `_workload_case_pair_anchor_expectations(...)` against `contract_case.expected_anchor_pairs`, `published_case_ids_by_signature(contract_case.correctness_case_signature)`, `contract_case.workload_signature`, `contract_case.include_workload`, and `contract_case.expected_anchor_pairs`; and
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases` still covers both `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` through `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` with the same anchored-case, unanchored-workload, and exact pair assertions.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n '^def (_compiled_pattern_module_success_anchor_lane|_compiled_pattern_module_compile_contract_anchor_lane)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the two wrapper helpers over introducing another detached helper family, support module, or registry layer.
- Preserve the current contract filenames, source-workload selection, anchored workload ids, correctness case ids, and callback/probe semantics exactly.

## Notes
- `RBR-1078` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1077`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1078` task file; and
  - `rg -n 'RBR-1078|RBR-1079|RBR-1080' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n '^def (_compiled_pattern_module_success_anchor_lane|_compiled_pattern_module_compile_contract_anchor_lane)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the two helper definitions at lines `17146` and `17170` in this run; and
  - each helper only repackages adjacent carrier data into `_CompiledPatternModuleContractAnchorLane(...)` for `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` returned `105 passed, 617 deselected` in this run.

## Completion Note
- Removed `_compiled_pattern_module_success_anchor_lane(...)` and `_compiled_pattern_module_compile_contract_anchor_lane(...)` from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and inlined `_CompiledPatternModuleContractAnchorLane(...)` construction directly inside `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`, preserving the same success-anchor and compile-contract carrier bindings.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` (`105 passed, 617 deselected`) and `bash -lc \"! rg -n '^def (_compiled_pattern_module_success_anchor_lane|_compiled_pattern_module_compile_contract_anchor_lane)\\\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py\"`.
