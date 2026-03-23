# RBR-1087: Collapse compiled-pattern compile-contract singleton lambdas

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining singleton lambda adapters in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` for the compiled-pattern `module.compile` contract surface so the shared compile-contract route and anchor-lane assembly read through named same-file helpers or direct existing carriers instead of six one-purpose anonymous wrappers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these singleton lambda adapters:
  - the five success-route lambdas currently passed into `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE` for `correctness_case_signature_builder`, `workload_signature_builder`, `include_workload_selector`, `cpython_dispatch`, and `callback_flags_selector`;
  - the compile-lane `expected_anchor_case_ids=(lambda manifest_path, contract_case=contract_case: ...)` wrapper currently created inside `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`.
- Replace that wrapper layer with named same-file helpers, or a strictly smaller equivalent, while keeping the existing route/case ownership surface intact:
  - `_CompiledPatternModuleCompileContractRoute`
  - `CompiledPatternModuleCompileContractCase`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Keep the current success-case behavior exactly intact after the cleanup:
  - the success route still uses `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SHARED_EXCLUDED_FIELDS`;
  - the success note text still remains the non-keyword `module.compile` note;
  - correctness/workload signature and workload inclusion still route through `_module_workflow_compiled_pattern_compile_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_compile_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_compile_workload(...)`;
  - CPython dispatch still uses `re.compile(re.compile(workload.pattern_payload(), workload.flags), workload.flags)`;
  - callback flags still remain `source_workload.flags`; and
  - the compile-contract anchor lane still resolves `_workload_case_pair_anchor_expectations(...)` against `contract_case.expected_anchor_pairs`.
- Keep the current compile-contract test surface intact:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation`
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases`
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing`
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n \"lambda _contract_case, case|lambda _contract_case, workload|include_workload_selector=lambda _contract_case, workload|cpython_dispatch=lambda _contract_case, workload|callback_flags_selector=lambda _contract_case, source_workload|lambda manifest_path, contract_case=contract_case\" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the singleton lambda layer over introducing another helper registry, support module, or detached contract abstraction.
- Keep the existing contract filenames, workload ids, anchored case ids, expected exceptions, callback behavior, and probe coverage intact.
- Do not broaden this into removing `_CompiledPatternModuleCompileContractRoute` entirely in the same run; keep the cleanup bounded to the anonymous-wrapper layer.

## Notes
- `RBR-1087` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1086`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1087` task file; and
  - `rg -n 'RBR-1087|RBR-1088|RBR-1089|RBR-1090' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n "lambda _contract_case, case|lambda _contract_case, workload|include_workload_selector=lambda _contract_case, workload|cpython_dispatch=lambda _contract_case, workload|callback_flags_selector=lambda _contract_case, source_workload|lambda manifest_path, contract_case=contract_case" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the five success-route singleton lambdas at lines `17082`, `17089`, `17093`, `17099`, and `17103`, plus the anchor-lane lambda at line `17232` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` returned `76 passed, 650 deselected` in this run.
