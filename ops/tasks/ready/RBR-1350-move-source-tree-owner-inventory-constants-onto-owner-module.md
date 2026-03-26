## RBR-1350: Move source-tree owner inventory constants onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining test-local owner-inventory tuples from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the source-tree owner boundary is described once on `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of being mirrored in the test suite.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add owner-owned inventory constants to `tests/benchmarks/source_tree_benchmark_anchor_support.py` for the slices that the test module still mirrors locally:
  - `SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `SOURCE_TREE_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES`
  - `SOURCE_TREE_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES`
  - `SOURCE_TREE_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES`
  - `SOURCE_TREE_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES`
  - `SOURCE_TREE_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to consume those owner-owned constants directly and delete these local mirror assignments:
  - `_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES`
  - `_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES`
  - `_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES`
  - `_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES`
  - `_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES`
- Keep the cleanup bounded to the source-tree owner inventory surface:
  - do not widen into `collection_replacement_benchmark_anchor_support.py`
  - keep `_COLLECTION_OWNER_SIGNATURE_HELPER_NAMES` local to the test module
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add a new helper module, wrapper layer, or alias shim

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata or compiled_pattern_module_success_owner_spec_surface_is_owned_locally or compiled_pattern_module_success_source_workload_params_follow_owner_specs or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the inventory data onto the existing owner module over creating another shared helper surface.
- Keep the source-tree boundary legible: the owner module should publish its own ownership inventories, and the test should read them instead of rebuilding the same tuples locally.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1350|RBR-1351|RBR-1352|RBR-1353' ops/state/current_status.md ops/state/backlog.md ops/tasks || true` returned only historical mentions inside completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- First candidate probe in this run found no remaining same-name duplicate top-level functions or assignments across `tests/benchmarks/source_tree_benchmark_anchor_support.py`, `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and `tests/benchmarks/benchmark_test_support.py`, so this follow-on is the first live bounded simplification that still remains.
- This target is live in the current checkout:
  - `rg -n '^(_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py` reports the six remaining local mirror constants on the test module
  - `rg -n '^SOURCE_TREE_(ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES|ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES|ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES|LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES|LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py` currently returns no matches because the owner module does not yet publish those inventories
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success_contract_builder_spec_uses_owner_metadata or compiled_pattern_module_success_owner_spec_surface_is_owned_locally or compiled_pattern_module_success_source_workload_params_follow_owner_specs or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `5 passed, 91 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^(_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_LOCAL_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPEC_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_LOCAL_FUNCTION_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_ALIAS_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES|_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_DEFINITION_NAMES)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because those six mirrored constants still live on the test module, and that failure belongs exactly to this cleanup
