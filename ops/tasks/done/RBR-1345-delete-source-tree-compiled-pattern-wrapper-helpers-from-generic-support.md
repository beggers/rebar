## RBR-1345: Delete source-tree compiled-pattern wrapper helpers from generic support

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-only compiled-pattern wrapper/helper block from `tests/benchmarks/benchmark_test_support.py` so the generic benchmark support module stops defining helpers that only repackage owner data already pinned on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Move the remaining source-tree-only compiled-pattern wrapper/helper surface out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `build_compiled_pattern_module_contract_anchor_lanes(...)`
  - `_build_compiled_pattern_module_compile_standard_benchmark_definitions(...)`
  - `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
  - `live_compiled_pattern_module_success_surface_ids(...)`
- Keep genuinely shared helpers and types in `tests/benchmarks/benchmark_test_support.py`:
  - do not widen into moving `CompiledPatternModuleCompileContractCase`, `_CompiledPatternModuleContractAnchorLane`, `build_compiled_pattern_module_compile_contract_cases(...)`, `build_compiled_pattern_module_compile_contract_source_workload_params(...)`, `include_live_compiled_pattern_module_success_workload(...)`, or the shared selector/signature helpers in the same task
  - the moved helper surface should build from those existing shared helpers instead of introducing another alias shim, wrapper layer, or helper module
- Update ownership checks so the split stays pinned:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should prove the moved wrapper/helper names are defined on `source_tree_benchmark_anchor_support.py`, not merely re-exported from `benchmark_test_support.py`
  - `tests/benchmarks/test_benchmark_test_support.py` should fail if `tests/benchmarks/benchmark_test_support.py` reintroduces those moved helper definitions
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add a new helper module, wrapper layer, or compatibility alias

## Verification
- `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module or wrong_text_model'`
- `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success_owner_spec_surface_is_owned_locally or compiled_pattern_module_compile_contract_builder_spec_builds_source_tree_contract or compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|_build_compiled_pattern_module_compile_standard_benchmark_definitions|live_compiled_pattern_module_success_surface_ids)\\b|^COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the task bounded to the four source-tree-only compiled-pattern wrapper/helper definitions that still live in the generic support module.
- Preserve the recent ownership direction: move the remaining wrapper/helper consumers toward `tests/benchmarks/source_tree_benchmark_anchor_support.py`; do not move the owner-spec data block back into `tests/benchmarks/benchmark_test_support.py`.

## Notes
- `RBR-1345` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1345|RBR-1346|RBR-1347|RBR-1348' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|_build_compiled_pattern_module_compile_standard_benchmark_definitions|live_compiled_pattern_module_success_surface_ids)\\b|^COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py` shows all four wrapper/helper definitions still live in `tests/benchmarks/benchmark_test_support.py`
  - `rg -n 'source_tree_support\\.(compiled_pattern_module_compile_contract_builder_spec|compiled_pattern_module_success_contract_builder_spec|compiled_pattern_module_helper_keyword_contract_builder_spec|_compiled_pattern_wrong_text_model_specs|_compiled_pattern_wrong_text_model_source_workloads|_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the remaining source-tree compiled-pattern contract/helper surface is already routed through `source_tree_support`, so this task can stay bounded to the generic wrapper/helper block without inventing a new abstraction
- Verification status in this planning run:
  - `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module or wrong_text_model'` passed with `20 passed, 119 deselected in 0.42s`
  - `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success_owner_spec_surface_is_owned_locally or compiled_pattern_module_compile_contract_builder_spec_builds_source_tree_contract or compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field'` passed with `6 passed, 88 deselected in 0.20s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|_build_compiled_pattern_module_compile_standard_benchmark_definitions|live_compiled_pattern_module_success_surface_ids)\\b|^COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because those source-tree-only wrapper/helper definitions still live in the generic support module, and that failure belongs exactly to this cleanup
- Completion note:
  - Moved `build_compiled_pattern_module_contract_anchor_lanes(...)`, `_build_compiled_pattern_module_compile_standard_benchmark_definitions(...)`, `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`, and `live_compiled_pattern_module_success_surface_ids(...)` from `tests/benchmarks/benchmark_test_support.py` to `tests/benchmarks/source_tree_benchmark_anchor_support.py`, while keeping the shared contract case/type/selectors in the generic support module.
  - Updated `tests/benchmarks/test_benchmark_test_support.py` to fail on any reintroduced generic definitions and updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to prove the moved names are locally defined in the source-tree owner module.
  - Verification in this run:
    - `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module or wrong_text_model'` passed with `21 passed, 119 deselected in 0.42s`
    - `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success_owner_spec_surface_is_owned_locally or compiled_pattern_module_compile_contract_builder_spec_builds_source_tree_contract or compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or compiled_pattern_module_helper_keyword_contract_builder_spec_handles_exception_field'` passed with `6 passed, 90 deselected in 0.24s`
    - `PYTHONPATH=. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile_wrapper_surface_is_owned_locally or compiled_pattern_module_compile_standard_benchmark_definitions_are_owned_locally_and_wrapper_free'` passed with `2 passed, 94 deselected in 0.24s`
    - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
    - `bash -lc "! rg -n '^def (build_compiled_pattern_module_contract_anchor_lanes|_build_compiled_pattern_module_compile_standard_benchmark_definitions|live_compiled_pattern_module_success_surface_ids)\\b|^COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py"` passed
