# RBR-1051: Collapse compiled-pattern `module.compile` success and keyword routes

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining parallel success-versus-keyword routing inside `CompiledPatternModuleCompileContractCase` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the bounded compiled-pattern `module.compile` contract surface derives that behavior through one canonical same-file route instead of nine `_uses_keyword_flags()` branches.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines `CompiledPatternModuleCompileContractCase._uses_keyword_flags(...)`, and `CompiledPatternModuleCompileContractCase` no longer contains any `if self._uses_keyword_flags()` branches.
- Replace the current success-versus-keyword branching with one canonical same-file route, or a strictly smaller equivalent, reused by:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE`
  - every case in `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`
- Keep the current success-case semantics intact while moving them onto that shared route:
  - the source-workload drift message still labels the surface as `success`;
  - excluded fields still remain exactly `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SHARED_EXCLUDED_FIELDS`;
  - the note text still remains the non-keyword `module.compile` note;
  - correctness/workload signature and include-workload selection still route through `_module_workflow_compiled_pattern_compile_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_compile_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_compile_workload(...)`;
  - payload round trips still preserve `haystack_text_model`; and
  - CPython dispatch still uses `re.compile(compiled_pattern, workload.flags)`, while callback flags still remain `source_workload.flags`.
- Keep the current keyword-case semantics intact while moving them onto that shared route:
  - the source-workload drift message still labels the surface as `keyword`;
  - excluded fields still add `categories` and `syntax_features` on top of `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SHARED_EXCLUDED_FIELDS`;
  - the note text still remains the `module.compile flags= keyword` note;
  - correctness/workload signature and include-workload selection still route through the keyword helpers with each case's `keyword_signature`, `allowed_patterns`, and `expected_exception`;
  - payload round trips still preserve `kwargs`, still preserve the concrete keyword `flags` carrier type, and still force `haystack_text_model` to `None`; and
  - CPython dispatch still uses `re.compile(compiled_pattern, **workload.keyword_arguments())`, while callback flags still remain `source_workload.keyword_arguments()["flags"]`.
- Update the existing compile-contract tests to use that shared route while preserving the current behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases`
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n 'def _uses_keyword_flags\\(|if self\\._uses_keyword_flags\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the parallel success-versus-keyword branching over introducing another support module, registry file, or checked-in data layer.
- Do not widen into compiled-pattern module-helper success routes, wrong-text-model owner specs, benchmark manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, reports, or tracked state prose.

## Notes
- `RBR-1051` is the next available unreserved task id in the current checkout:
  - the task queues currently top out at `RBR-1050`; and
  - `rg -n 'RBR-1051|RBR-1052|RBR-1053|RBR-1054' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `CompiledPatternModuleCompileContractCase` still defines `def _uses_keyword_flags(...)` at line `16862`;
  - the class still fans the same success-versus-keyword split across eight `if self._uses_keyword_flags()` branches at lines `16878`, `16886`, `16897`, `16908`, `16919`, `16943`, `16959`, and `16964`; and
  - those branches still drive source-workload selection, payload-round-trip expectations, signature routing, and callback/CPython dispatch for the same compile-contract surface.
- The focused pytest slice in Verification already passes in the current checkout (`74 passed, 647 deselected in 0.22s`), and the negative `rg` check fails only because the targeted branch fanout still exists.

## Completion Note
- 2026-03-23: Added a shared file-local `_CompiledPatternModuleCompileContractRoute` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rewired `CompiledPatternModuleCompileContractCase` so the success case and every keyword case delegate drift labeling, excluded fields, notes, signature selection, workload inclusion, payload round trips, CPython dispatch, and callback flags through that route instead of branching on `_uses_keyword_flags()`.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` (`74 passed, 647 deselected in 0.67s`).
- Verified branch removal with `bash -lc "! rg -n 'def _uses_keyword_flags\\(|if self\\._uses_keyword_flags\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
