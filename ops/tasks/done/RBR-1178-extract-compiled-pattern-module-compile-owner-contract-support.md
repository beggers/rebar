# RBR-1178: Extract compiled-pattern module.compile owner contract support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern `module.compile` owner-spec inventory and dedicated owner-contract test surface that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by extending the existing compiled-pattern compile benchmark support files, so the giant combined benchmark suite stops owning a second compile-contract lane after the shared route/case support already moved out.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` so it owns the remaining compiled-pattern `module.compile` owner inventory that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_CompiledPatternModuleCompileKeywordOwnerSpec`;
  - move `_CompiledPatternModuleCompileSuccessOwnerSpec`;
  - move `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`;
  - move `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`;
  - move `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`;
  - move `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`; and
  - move `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`.
- Keep the extracted support pinned to the current live compiled-pattern `module.compile` surface instead of widening the contract family:
  - preserve the current anchor-definition names, allowed-pattern sets, contract filenames, anchor-contract filenames, expected anchor pairs, and bounded ignorecase rejection payloads;
  - preserve the existing source-workload ordering and `-contract` workload ids for both success and `flags=` keyword rows; and
  - keep the current `module.compile` build-call expectations, callback flag materialization, and correctness-anchor mapping unchanged.
- Move the dedicated compiled-pattern `module.compile` owner-contract tests out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and into `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` without copying the giant combined suite:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation(...)`;
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases(...)`;
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(...)`;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads(...)`; and
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing(...)`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved compile-owner support instead of defining that block inline:
  - keep `test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points(...)` and `test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(...)` on the same rows and expectations;
  - keep the adjacent `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(...)` behavior unchanged; and
  - delete the moved owner-spec/test block from the combined file instead of leaving wrapper aliases behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, reports, or tracked ops state prose.
- Prefer deleting the inline compiled-pattern `module.compile` owner-spec/test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving local wrapper aliases there.
- Do not widen this task into compiled-pattern module-helper keyword support, wrong-text-model owner support, source-tree contract-builder support, standard benchmark anchor support, or unrelated pattern-window keyword/indexlike cleanup.

## Notes
- `RBR-1178` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1178|compiled_pattern_module_compile_benchmark_support" ops/tasks ops/state/backlog.md ops/state/current_status.md -g '*.md'` matched only historical `compiled_pattern_module_compile` task history and did not reveal a live reservation or sibling task at `RBR-1178`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is still concrete and cross-file in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `19415` lines in this run;
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` is `668` lines and `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` is `163` lines, so the dedicated support surface remains much smaller than the combined suite that still owns the owner-spec/test block;
  - `rg -n "^class _CompiledPatternModuleCompileKeywordOwnerSpec|^class _CompiledPatternModuleCompileSuccessOwnerSpec|^_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS =|^_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS =|^def test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation\\(|^def test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases\\(|^def test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time\\(|^def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads\\(|^def test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still shows the owner block at lines `8036`, `8111`, `8154`, `8210`, `16939`, `17006`, `17052`, `17097`, and `17130`; and
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(...)` starts immediately after that block at line `17175`, so this cleanup should stop at the compile-owner surface instead of widening into adjacent helper-keyword support.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` returned `78 passed` in this run after the dedicated compile-owner contract tests moved into that file.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'` returned `15 passed, 619 deselected, 22 subtests passed` in this run.

## Completion
- Moved the compiled-pattern `module.compile` owner-spec inventory and the prebuilt compile contract constants into `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, keeping the existing filenames, workload ids, anchor pairs, callback flag materialization, and bounded ignorecase rejection payloads unchanged.
- Moved the five dedicated compiled-pattern `module.compile` owner-contract tests into `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` and deleted the inline owner-contract/test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
