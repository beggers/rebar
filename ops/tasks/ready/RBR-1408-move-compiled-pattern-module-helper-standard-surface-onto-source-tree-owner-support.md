## RBR-1408: Move the compiled-pattern module-helper standard surface onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-owned compiled-pattern module-helper standard benchmark surface from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still owns the compiled-pattern module-helper route/selectors and the `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` tuple even though the live consumers are the source-tree owner support module plus the benchmark-owner inventory tests that verify the combined source-tree benchmark surface.
- Move that one owner seam onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only generic helpers and neutral contract primitives instead of another source-tree-specific standard-definition lane.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete this source-tree-owned compiled-pattern module-helper surface from `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS`
  - `_compiled_pattern_module_helper_route(...)`
  - `_module_workflow_compiled_pattern_success_correctness_case_signature(...)`
  - `_module_workflow_compiled_pattern_workload_args(...)`
  - `_module_workflow_compiled_pattern_success_workload_signature(...)`
  - `_is_module_workflow_compiled_pattern_workload(...)`
  - `_is_module_workflow_compiled_pattern_literal_success_workload(...)`
  - `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(...)`
  - `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload(...)`
  - `_is_collection_replacement_compiled_pattern_success_workload(...)`
  - `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
- Recreate that moved surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wired to the existing shared primitives it still needs, without changing the helper route behavior, workload-selection semantics, standard benchmark definition names, or expected anchored case ids.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the ownership assertions and combined-definition inventory treat the moved compiled-pattern module-helper surface as source-tree-owned instead of shared-support-owned.
- Update `tests/benchmarks/test_benchmark_test_support.py` so shared-support ownership assertions stop treating the moved compiled-pattern module-helper surface as benchmark-support-owned and instead verify that the moved route/selectors/definition tuple now live on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` only as needed so its explicit standard-definition inventory imports the moved compiled-pattern module-helper definition tuple from source-tree owner support instead of shared support.
- Keep `benchmark_test_support.py` owning only genuinely shared helpers used by this slice, such as:
  - `freeze_signature_value(...)`
  - `selected_manifest_workloads(...)`
  - `run_benchmark_workload_with_cpython(...)`
  - `StandardBenchmarkAnchorContractDefinition`
  - `compiled_pattern_contract_expected_build_calls(...)`
- Do not widen into the collection-replacement keyword-contract layer, compile-owner routes, pattern-boundary owner support, workload manifests, generated reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_helper_owner_surface or compiled_pattern_module_helper_route or wrong_text_model_selector'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_standard_definitions_export_stays_owned_by_source_tree'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'owner_surface or wrong_text_model or module_helper_standard_benchmark_definitions or manifest_path'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(def _compiled_pattern_module_helper_route|def _module_workflow_compiled_pattern_success_correctness_case_signature|def _module_workflow_compiled_pattern_workload_args|def _module_workflow_compiled_pattern_success_workload_signature|def _is_module_workflow_compiled_pattern_workload|def _is_module_workflow_compiled_pattern_literal_success_workload|def _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|def _is_module_workflow_compiled_pattern_verbose_bytes_success_workload|def _is_collection_replacement_compiled_pattern_success_workload|_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS =|_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS =|_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS =|COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS =)' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1408\\b|RBR-1409\\b|RBR-1410\\b" ops/state/backlog.md ops/state/current_status.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1408`; the only hit was the completed `RBR-1407` task note.
- Candidate selection in this run:
  - The first post-JSON probe was the remaining collection/replacement seam in `tests/benchmarks/benchmark_test_support.py`, but that surface still straddles collection-owner and source-tree-owner behavior, so it was not the cleanest single-owner task to queue next.
  - The second bounded probe was the source-tree compiled-pattern module-helper standard-definition seam, which is still explicitly shared-support-owned today even though the owner inventory and route checks live under `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
  - `rg -n "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS|_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|_compiled_pattern_module_helper_route|_is_module_workflow_compiled_pattern_workload|_is_collection_replacement_compiled_pattern_success_workload" tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` shows the remaining route/selectors/definition tuple still originate in `tests/benchmarks/benchmark_test_support.py`.
  - `sed -n '3780,4105p' tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the current source-tree ownership tests still expect those names to arrive through `benchmark_test_support`, which is the exact seam this task should eliminate.
  - I stopped after the second candidate because this one removes one remaining reusable owner-boundary layer from the shared benchmark-support file without widening into the keyword-contract surface.
- Verification in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_helper_owner_surface or compiled_pattern_module_helper_route or wrong_text_model_selector'` -> `7 passed, 173 deselected`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_standard_definitions_export_stays_owned_by_source_tree'` -> `1 passed, 119 deselected`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'owner_surface or wrong_text_model or module_helper_standard_benchmark_definitions or manifest_path'` -> `23 passed, 132 deselected`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> passed
