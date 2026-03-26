## RBR-1410: Move the compiled-pattern module-compile contract owner layer onto source-tree support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining source-tree-owned compile-contract layer from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the compiled-pattern `module.compile` owner tuples and standard-definition export, but `tests/benchmarks/benchmark_test_support.py` still owns the route dataclasses, owner-spec builders, contract-case builders, and compile-specific constants that only feed that source-tree lane.
- Move that compile-contract owner layer onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only generic helpers and neutral contract primitives instead of another source-tree-specific contract builder seam.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete this compiled-pattern `module.compile` owner-only surface from `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE`
  - `_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE`
  - `_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE`
  - `_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION`
  - `_CompiledPatternModuleCompileContractRoute`
  - `CompiledPatternModuleCompileContractCase`
  - `_CompiledPatternModuleContractAnchorLane`
  - `_compiled_pattern_module_compile_success_owner_specs(...)`
  - `_compiled_pattern_module_compile_keyword_owner_specs(...)`
  - `build_compiled_pattern_module_compile_contract_cases(...)`
  - `build_compiled_pattern_module_compile_contract_source_workload_params(...)`
  - `build_compiled_pattern_module_contract_anchor_lanes(...)`
- Recreate that moved surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wired to the existing shared generic helpers it still needs, without changing:
  - the eight compiled-pattern `module.compile` anchor-definition names and ordering,
  - the `case_id` values for the contract cases,
  - the expected anchor pairs and source workload ids,
  - the success versus keyword route behavior,
  - the ignorecase rejection payload expectations.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so ownership assertions and type references treat `CompiledPatternModuleCompileContractCase` and the compile-contract builder layer as source-tree-owned instead of shared-support-owned.
- Update `tests/benchmarks/test_benchmark_manifest_validation.py` so its compile-contract validation tests type against the moved source-tree-owned case class rather than importing that owner type from `benchmark_test_support`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so shared-support ownership assertions stop expecting the moved compile-contract owner layer on `benchmark_test_support.py` and instead verify it lives on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`, including the compile workload selectors, payload round-trip assertions, CPython dispatch helpers, generic signature builders, `StandardBenchmarkAnchorContractDefinition`, `_SourceTreeContractBuilderSpec`, and `compiled_pattern_contract_expected_build_calls(...)`.
- Do not widen into the compiled-pattern module-helper lane, collection/replacement keyword-contract surfaces, pattern-boundary owner support, benchmark manifests, reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_compile'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc \"! rg -n '^(class _CompiledPatternModuleCompileContractRoute|class CompiledPatternModuleCompileContractCase|class _CompiledPatternModuleContractAnchorLane|def _compiled_pattern_module_compile_success_owner_specs|def _compiled_pattern_module_compile_keyword_owner_specs|def build_compiled_pattern_module_compile_contract_cases|def build_compiled_pattern_module_compile_contract_source_workload_params|def build_compiled_pattern_module_contract_anchor_lanes|_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION =)' tests/benchmarks/benchmark_test_support.py\"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1410\\b" ops/state/backlog.md ops/state/current_status.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1410`; the only hit was historical note text inside completed `RBR-1408`.
- Candidate selection in this run:
  - The first viable post-JSON simplification was the remaining compiled-pattern `module.compile` contract owner layer because `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the downstream tuples and standard definitions while `tests/benchmarks/benchmark_test_support.py` still owns the route, case, lane, and builder machinery.
  - `rg -n "CompiledPatternModuleCompileContractCase|build_compiled_pattern_module_compile_contract_cases|build_compiled_pattern_module_compile_contract_source_workload_params|build_compiled_pattern_module_contract_anchor_lanes|_compiled_pattern_module_compile_success_owner_specs|_compiled_pattern_module_compile_keyword_owner_specs" -g '*.py'` shows those names are defined only in `tests/benchmarks/benchmark_test_support.py` and consumed from `tests/benchmarks/source_tree_benchmark_anchor_support.py` plus the scoped benchmark-owner tests.
  - I stopped after this first viable candidate because it removes one complete owner-boundary helper layer from the shared benchmark-support module without depending on unrelated feature work.
- Verification in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_compile'` -> `36 passed, 331 deselected`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py` was not rerun in this planning pass, so the implementation run should execute it after making the move.
  - `bash -lc "! rg -n '^(class _CompiledPatternModuleCompileContractRoute|class CompiledPatternModuleCompileContractCase|class _CompiledPatternModuleContractAnchorLane|def _compiled_pattern_module_compile_success_owner_specs|def _compiled_pattern_module_compile_keyword_owner_specs|def build_compiled_pattern_module_compile_contract_cases|def build_compiled_pattern_module_compile_contract_source_workload_params|def build_compiled_pattern_module_contract_anchor_lanes|_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION =)' tests/benchmarks/benchmark_test_support.py"` currently fails only because this exact owner layer is still present, which is the cleanup this task queues.

## Completion Notes
- Moved the compiled-pattern `module.compile` contract owner layer from `tests/benchmarks/benchmark_test_support.py` into `tests/benchmarks/source_tree_benchmark_anchor_support.py`, including the compile-specific constants, owner-spec classes/builders, route/case/lane dataclasses, and contract-case/anchor-lane builders.
- Left the generic compile signature, payload round-trip, and CPython dispatch helpers in shared benchmark support, and updated their type annotations to stay owner-neutral.
- Updated the source-tree and manifest-validation tests to type against `source_tree_benchmark_anchor_support.CompiledPatternModuleCompileContractCase`, and refreshed the benchmark-support ownership assertions to verify the moved surface is absent from shared support and present on the source-tree support module.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile' tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_compile'` -> `37 passed, 331 deselected`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
  - `bash -lc "! rg -n '^(class _CompiledPatternModuleCompileContractRoute|class CompiledPatternModuleCompileContractCase|class _CompiledPatternModuleContractAnchorLane|def _compiled_pattern_module_compile_success_owner_specs|def _compiled_pattern_module_compile_keyword_owner_specs|def build_compiled_pattern_module_compile_contract_cases|def build_compiled_pattern_module_compile_contract_source_workload_params|def build_compiled_pattern_module_contract_anchor_lanes|_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE =|_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS =|_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION =)' tests/benchmarks/benchmark_test_support.py"`
