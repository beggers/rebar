## RBR-1273: Move compiled-pattern helper keyword contract support onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining support-owned contract surface that still lives inside `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`, so the compiled-pattern helper benchmark layer keeps contract specs, workload inventories, and param builders in its existing owner support module instead of inside an 853-line test file.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` so it becomes the single owner of the compiled-pattern helper keyword contract support surface currently defined in the test module:
  - `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)`
  - `_is_collection_replacement_compiled_pattern_module_helper_keyword_workload(...)`
  - `_CompiledPatternModuleHelperKeywordContractSpec`
  - `_CompiledPatternModuleHelperKeywordContractSurface`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS`
- Update `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` to import and use that support-owned surface instead of defining the contract specs, surfaces, workload-order drift guards, and parametrization tuples locally.
- Preserve current behavior exactly:
  - keep the same contract filenames, note text, manifest ids, timed-sample counts, expected source workload ids, precompile anchor ids, and payload drop fields;
  - keep `contract_builder_spec()`, `expected_materialized_field_names()`, `source_workloads()`, `precompile_source_workloads()`, `expected_build_calls()`, `expected_callback_call()`, `expected_callback_result()`, `run_cpython_helper_workload()`, `assert_outcome()`, and `assert_payload_round_trip()` returning the same results as before; and
  - keep the existing compiled-pattern helper route and collection-replacement keyword helpers as the underlying behavior owners instead of adding a new registry, generic contract layer, or compatibility wrapper.
- Keep the cleanup structural and bounded to the two files above. Do not widen it into harness implementation code, workload manifests, README/state docs, or another new support module.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `bash -lc "! rg -n 'class _CompiledPatternModuleHelperKeywordContractSpec|class _CompiledPatternModuleHelperKeywordContractSurface|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS\\s*=' tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py"`

## Constraints
- Prefer consolidating onto the existing `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` owner module over creating another helper/support file. The point is to finish the ownership move, not to add a fresh abstraction layer.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`.
- Do not change helper-keyword workload selection, callback dispatch behavior, contract payload shape, or assertion semantics in this task.

## Notes
- `RBR-1273` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1273|RBR-1274|RBR-1275|RBR-1276|RBR-1277" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` is `853` lines in this run and still defines the helper-keyword contract dataclasses, workload inventories, and parametrization tuples locally;
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` is only `256` lines and already owns the adjacent compiled-pattern helper route/selectors that the keyword contract surface depends on; and
  - `bash -lc "! rg -n 'class _CompiledPatternModuleHelperKeywordContractSpec|class _CompiledPatternModuleHelperKeywordContractSurface|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS\\s*=|_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS\\s*=' tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py"` currently fails because that support surface still lives in the test module, and that failure belongs to the exact cleanup queued here.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` passed with `133 passed`; and
  - the negative `rg` check in `Verification` currently fails for the expected reason described above.
