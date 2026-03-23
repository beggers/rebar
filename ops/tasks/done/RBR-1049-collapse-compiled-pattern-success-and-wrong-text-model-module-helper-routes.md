## RBR-1049: Collapse compiled-pattern success and wrong-text-model module-helper routes

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining duplicate compiled-pattern module-helper callback-result, callback-call, and CPython-dispatch routing from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the bounded success and wrong-text-model contract surfaces derive that behavior through one canonical same-file route instead of parallel owner-spec branches.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` adds one canonical same-file route for the compiled-pattern module-helper operation surface, or a strictly smaller equivalent, reused by:
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC`
- Repoint the current duplicate compiled-pattern routing through that shared route instead of leaving it split across:
  - `CompiledPatternModuleSuccessOwnerSpec.expected_callback_result(...)`
  - `CompiledPatternModuleSuccessOwnerSpec.expected_callback_call(...)`
  - the `self.use_compiled_pattern` branch of `WrongTextModelOwnerSpec.expected_callback_result(...)`
  - the `self.use_compiled_pattern` branch of `WrongTextModelOwnerSpec.expected_callback_call(...)`
  - the `self.use_compiled_pattern` branch of `WrongTextModelOwnerSpec.run_cpython_workload(...)`
- Keep the current collection/replacement success callback semantics intact while moving them onto that shared route:
  - `module.split` still expects `(operation, haystack_payload(), maxsplit_argument(), flags, {})`;
  - `module.findall` and `module.finditer` still expect `(operation, haystack_payload(), flags)`;
  - `module.sub` and `module.subn` still expect `(operation, replacement_payload(), haystack_payload(), count_argument(), flags, {})`;
  - `module.finditer` still returns `["module-finditer-result"]`;
  - `module.subn` still returns `("module-result", 0)`; and
  - the other success operations still return `"module-result"`.
- Keep the current module-boundary success callback semantics intact while moving them onto that shared route:
  - `module.search`, `module.match`, and `module.fullmatch` still expect `(operation, haystack_payload(), 0, {})`; and
  - those success operations still return `"module-result"`.
- Keep the current compiled-pattern wrong-text-model CPython-dispatch semantics intact while moving them onto that shared route:
  - the route still compiles `re.compile(workload.pattern_payload(), workload.flags)` before helper dispatch;
  - wrong-text-model `module.split` still dispatches the compiled pattern plus `haystack_payload()` and `maxsplit_argument()`;
  - wrong-text-model `module.findall` still dispatches the compiled pattern plus `haystack_payload()` and `workload.flags`;
  - wrong-text-model `module.finditer` still dispatches the same arguments and still materializes `list(...)`;
  - wrong-text-model `module.sub` and `module.subn` still dispatch the compiled pattern plus `replacement_payload()`, `haystack_payload()`, and `count_argument()`; and
  - wrong-text-model `module.search`, `module.match`, and `module.fullmatch` still dispatch the compiled pattern plus `haystack_payload()` and `workload.flags`.
- Update the existing contract call sites to use that shared route while preserving the current behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads`
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing`
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting duplicated compiled-pattern module-helper routing over introducing another detached abstraction layer.
- Do not widen into direct-pattern wrong-text-model routes, compiled-pattern keyword-contract surfaces, `module.compile` contract cases, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, reports, or tracked state prose.

## Notes
- `RBR-1049` is the next available unreserved task id in the current checkout:
  - `find ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 5` currently ends at `RBR-1048-catch-up-module-sub-str-count-one-singleton.md`; and
  - `rg -n 'RBR-1049|RBR-1050|RBR-1051|RBR-1052' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `CompiledPatternModuleSuccessOwnerSpec.expected_callback_result(...)` and `.expected_callback_call(...)` still hold the success-side compiled-pattern routing at lines `16310` and `16324`;
  - `WrongTextModelOwnerSpec.expected_callback_result(...)`, `.expected_callback_call(...)`, and `.run_cpython_workload(...)` still hold the wrong-text-model compiled-pattern routing at lines `17464`, `17515`, and `17593`; and
  - the focused pytest slice in Verification already passes (`87 passed, 634 deselected in 0.19s`), so the acceptance surface is isolated from unrelated drift.

## Completion Note
- 2026-03-23: Added one shared `_compiled_pattern_module_helper_route(...)` plus `_run_compiled_pattern_module_helper_workload_with_cpython(...)` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and repointed the compiled-pattern success and wrong-text-model owner specs through that same file-local route for callback results, callback calls, and wrong-text-model CPython helper dispatch.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'` (`87 passed, 634 deselected`).
