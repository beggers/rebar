# RBR-1054: Collapse the compiled-pattern `module.compile` keyword wrapper family

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining six-variant keyword wrapper family in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern `module.compile` keyword owner path derives its literal, named-group, and rejection slices through one canonical same-file spec surface instead of eighteen near-identical selector/signature wrappers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these keyword-specific wrapper functions:
  - `def _module_workflow_compiled_pattern_compile_int_zero_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_int_zero_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload(...)`
  - `def _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload(...)`
  - `def _module_workflow_compiled_pattern_compile_bool_false_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_bool_false_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload(...)`
  - `def _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload(...)`
  - `def _module_workflow_compiled_pattern_compile_ignorecase_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_ignorecase_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload(...)`
  - `def _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_correctness_case_signature(...)`
  - `def _module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload_signature(...)`
  - `def _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload(...)`
- Replace that wrapper family with one explicit same-file spec route, or a strictly smaller equivalent, that owns the per-slice fields once and is reused by both of these consumers:
  - the six compiled-pattern `module.compile` keyword `StandardBenchmarkAnchorContractDefinition` entries in the module-boundary anchor section;
  - the six entries in `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`.
- Keep the current six keyword slices intact while routing them through that shared spec surface:
  - `int-zero`
  - `int-zero-named-group`
  - `bool-false`
  - `bool-false-named-group`
  - `ignorecase`
  - `ignorecase-named-group`
- Preserve the current per-slice semantics exactly after the refactor:
  - `int-zero` and `int-zero-named-group` still use `_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE`;
  - `bool-false` and `bool-false-named-group` still use `_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE`;
  - `ignorecase` and `ignorecase-named-group` still use `_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE` plus `_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION`;
  - literal slices still remain pinned to `_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS`;
  - named-group slices still remain pinned to `_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS`;
  - the six anchor-definition names, expected anchor pairs, contract filenames, anchor contract filenames, and `run_callback_result_parity=True` behavior all stay unchanged; and
  - `CompiledPatternModuleCompileContractCase` keyword cases still expose the same `case_id`, `keyword_signature`, `allowed_patterns`, and `expected_exception` values as they do today.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc \"! rg -n '^def (_module_workflow_compiled_pattern_compile_(int_zero|bool_false|ignorecase).*(correctness_case_signature|workload_signature)|_is_module_workflow_compiled_pattern_compile_(int_zero|bool_false|ignorecase).*)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py\"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the repeated wrapper family over introducing another support module, registry file, generated artifact, or checked-in data layer.
- Do not widen into benchmark manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, implementation code, reports, or tracked state prose.

## Notes
- `RBR-1054` is the next available unreserved task id in the current checkout:
  - `RBR-1053` is already occupied by the live feature task in `ops/tasks/ready/RBR-1053-publish-module-subn-bytes-single-match.md`; and
  - `rg -n 'RBR-1054|RBR-1055|RBR-1056|RBR-1057' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the newest runtime dashboard shows no inherited-dirty checkpoint churn or stalled post-task refresh path; and
  - the scoped benchmark-contract verification command above already passes in the live checkout (`75 passed, 646 deselected, 18 subtests passed`).
- The duplication target is concrete in the live checkout:
  - the repeated keyword wrapper definitions currently sit contiguously at lines `7522` through `7706` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - the same family is consumed once in the standard anchor-definition section at lines `9754` through `9894`; and
  - the same family is consumed again in `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS` at lines `17227` through `17353`.

## Completion Note
- 2026-03-23: Replaced the six compiled-pattern `module.compile` keyword wrapper triplets with one file-local `_CompiledPatternModuleCompileKeywordOwnerSpec` family in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, then reused those specs for the six module-boundary `StandardBenchmarkAnchorContractDefinition` entries, the six `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS` entries, and the measured-row assertion in the same file.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'` (`75 passed, 646 deselected, 18 subtests passed in 1.77s`).
- Verified wrapper removal with `bash -lc "! rg -n '^def (_module_workflow_compiled_pattern_compile_(int_zero|bool_false|ignorecase).*(correctness_case_signature|workload_signature)|_is_module_workflow_compiled_pattern_compile_(int_zero|bool_false|ignorecase).*)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
