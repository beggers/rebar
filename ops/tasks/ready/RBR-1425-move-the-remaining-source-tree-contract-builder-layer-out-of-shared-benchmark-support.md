## RBR-1425: Move the remaining source-tree contract-builder layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree contract-builder owner layer from `tests/benchmarks/benchmark_test_support.py`.
- `benchmark_test_support.py` still owns `_SourceTreeContractBuilderSpec`, `_source_tree_contract_manifest(...)`, `_source_tree_contract_workload(...)`, the wrong-text-model contract specs, and the compiled-pattern module compile owner-spec registries even though that surface is only consumed by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the meta-tests that police that boundary.
- Keep the shared support module focused on reusable benchmark utilities; make the combined source-tree owner suite hold its own contract-builder types, specs, and local registries directly.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree contract-builder owner surface out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including:
  - `_SourceTreeContractBuilderSpec`
  - `_source_tree_contract_manifest(...)`
  - `_source_tree_contract_workload(...)`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS`
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `CompiledPatternModuleCompileContractCase`
  - `_CompiledPatternModuleContractAnchorLane`
  - `_CompiledPatternModuleCompileKeywordOwnerSpec`
  - `_CompiledPatternModuleCompileSuccessOwnerSpec`
  - `build_compiled_pattern_module_compile_contract_cases(...)`
  - `build_compiled_pattern_module_compile_contract_source_workload_params(...)`
  - `build_compiled_pattern_module_contract_anchor_lanes(...)`
  - `_compiled_pattern_module_compile_success_owner_specs(...)`
  - `_compiled_pattern_module_compile_keyword_owner_specs(...)`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Rewrite the combined source-tree suite to use that contract-builder surface as local owner definitions instead of reaching through `benchmark_test_support`.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the simpler boundary:
  - `benchmark_test_support.py` no longer exports the moved source-tree contract-builder layer
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved definitions/registries locally
  - genuinely shared helpers still route through the existing `benchmark_test_support` module alias
- Keep `tests/benchmarks/benchmark_test_support.py` limited to reusable benchmark utilities after the move; do not reopen workload manifests, `python/rebar_harness/benchmarks.py`, reports, or project-state files.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or wrong_text_model'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or compiled_pattern_module_compile'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^class _SourceTreeContractBuilderSpec|^def _source_tree_contract_workload\\(|^def _source_tree_contract_manifest\\(|^class CompiledPatternModuleCompileContractCase|^class _CompiledPatternModuleContractAnchorLane|^class _CompiledPatternModuleCompileKeywordOwnerSpec|^class _CompiledPatternModuleCompileSuccessOwnerSpec|^class CompiledPatternModuleSuccessOwnerSpec|^def build_compiled_pattern_module_compile_contract_cases\\(|^def build_compiled_pattern_module_compile_contract_source_workload_params\\(|^def build_compiled_pattern_module_contract_anchor_lanes\\(|^def _compiled_pattern_module_compile_success_owner_specs\\(|^def _compiled_pattern_module_compile_keyword_owner_specs\\(|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC\\s*=|^_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES\\s*=' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1425|RBR-1426|RBR-1427" ops/state/backlog.md ops/state/current_status.md` returned no planning-owned reservation for `RBR-1425`.
- Candidate selection in this run:
  - `tests/benchmarks/benchmark_test_support.py` still owns the source-tree contract-builder primitives and the compiled-pattern module compile owner registries at lines currently matched by `rg -n "^class _SourceTreeContractBuilderSpec|^def _source_tree_contract_workload\\(|^def _source_tree_contract_manifest\\(|^class CompiledPatternModuleCompileContractCase|^class _CompiledPatternModuleContractAnchorLane|^class _CompiledPatternModuleCompileKeywordOwnerSpec|^class _CompiledPatternModuleCompileSuccessOwnerSpec|^class CompiledPatternModuleSuccessOwnerSpec|^def build_compiled_pattern_module_compile_contract_cases\\(|^def build_compiled_pattern_module_compile_contract_source_workload_params\\(|^def build_compiled_pattern_module_contract_anchor_lanes\\(|^def _compiled_pattern_module_compile_success_owner_specs\\(|^def _compiled_pattern_module_compile_keyword_owner_specs\\(|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC\\s*=|^_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES\\s*=" tests/benchmarks/benchmark_test_support.py"`.
  - The only non-meta consumer is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, which currently imports the support module and reaches through it for that owner-specific surface instead of owning it locally.
  - That makes this a bounded post-JSON architectural cleanup: delete one remaining shared owner layer rather than continuing to preserve source-tree-only contract-building machinery in the common support module.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or wrong_text_model'` passed with `100 passed, 207 deselected in 1.69s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or compiled_pattern_module_compile'` currently fails in `test_source_tree_contract_builder_spec_constructor_sites_stay_owner_scoped`, which is already stale inside this exact source-tree contract-builder boundary and should be rewritten as part of this cleanup.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n "^class _SourceTreeContractBuilderSpec|^def _source_tree_contract_workload\\(|^def _source_tree_contract_manifest\\(|^class CompiledPatternModuleCompileContractCase|^class _CompiledPatternModuleContractAnchorLane|^class _CompiledPatternModuleCompileKeywordOwnerSpec|^class _CompiledPatternModuleCompileSuccessOwnerSpec|^class CompiledPatternModuleSuccessOwnerSpec|^def build_compiled_pattern_module_compile_contract_cases\\(|^def build_compiled_pattern_module_compile_contract_source_workload_params\\(|^def build_compiled_pattern_module_contract_anchor_lanes\\(|^def _compiled_pattern_module_compile_success_owner_specs\\(|^def _compiled_pattern_module_compile_keyword_owner_specs\\(|^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC\\s*=|^_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES\\s*=|^_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS\\s*=|^_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES\\s*=" tests/benchmarks/benchmark_test_support.py` currently finds the exact support-owned layer this task deletes.
