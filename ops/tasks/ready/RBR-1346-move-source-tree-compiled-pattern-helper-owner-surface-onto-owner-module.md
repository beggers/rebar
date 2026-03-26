## RBR-1346: Move source-tree compiled-pattern helper owner surface onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only compiled-pattern helper owner-surface block from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops owning helper benchmark definitions and owner-specific wrong-text-model metadata that already belong with `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only compiled-pattern helper owner-surface names out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`
  - `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)`
  - `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
- Keep genuinely shared compiled-pattern helper machinery in `tests/benchmarks/benchmark_test_support.py`:
  - do not widen into moving `_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS`, `_compiled_pattern_module_helper_route(...)`, `_run_cpython_compiled_pattern_module_helper_workload(...)`, `_module_workflow_compiled_pattern_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_workload_signature(...)`, `_is_module_workflow_compiled_pattern_workload(...)`, `_is_module_workflow_compiled_pattern_literal_success_workload(...)`, `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(...)`, `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload(...)`, `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, or `include_live_compiled_pattern_module_success_workload(...)` in the same task
  - the moved owner surface should build from those existing shared helpers instead of adding another alias shim, wrapper layer, or helper module
- Update the remaining live consumer in `tests/benchmarks/benchmark_test_support.py` so `STANDARD_BENCHMARK_DEFINITIONS` pulls the compiled-pattern helper owner block from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of a local assignment.
- Tighten ownership checks so this split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the moved helper owner-surface names are defined on `source_tree_benchmark_anchor_support.py`, not merely re-exported from `benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces that moved helper owner-surface block
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add a new helper module, alias shim, or compatibility wrapper

## Verification
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_helper_surface or standard_benchmark_definitions_keep_owner_blocks_in_order or wrong_text_model_selector'`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_surface_locally or compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS)\\b|^def _is_module_workflow_compiled_pattern_wrong_text_model_workload\\b' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the remaining source-tree-only compiled-pattern helper owner-surface block and its direct ownership checks.
- Prefer moving the existing owner-specific assignments and selector onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over rebuilding the same surface behind another wrapper.

## Notes
- `RBR-1346` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1346|RBR-1347|RBR-1348|RBR-1349' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^(_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS)\\b|^def _is_module_workflow_compiled_pattern_wrong_text_model_workload\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py` shows all four owner-surface names still defined in `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the adjacent compiled-pattern module compile owner surface, wrong-text-model contract specs, and contract-builder helpers, so this follow-on stays on the same ownership seam instead of creating a new layer
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_helper_surface or standard_benchmark_definitions_keep_owner_blocks_in_order or wrong_text_model_selector'` passed with `10 passed, 130 deselected in 0.15s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_surface_locally or compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata'` passed with `3 passed, 93 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS)\\b|^def _is_module_workflow_compiled_pattern_wrong_text_model_workload\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because that source-tree-only helper owner-surface block still lives in the generic support module, and that failure belongs exactly to this cleanup
