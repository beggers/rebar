## RBR-1406: Move the compiled-pattern module-compile owner surface onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-only compiled-pattern module-compile owner surface from `tests/benchmarks/benchmark_test_support.py`.
- The shared support module still owns `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`, `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`, `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`, `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`, and `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` even though their live consumers are the source-tree owner suites plus manifest-validation coverage for that same owner slice.
- Move that owner surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only the neutral builders, dataclasses, and generic helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Delete these source-tree-only owner assignments from `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
- Recreate that owner surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, building it from the existing shared dataclasses/builders in `tests/benchmarks/benchmark_test_support.py` instead of adding another wrapper layer or re-exporting the moved assignments back through shared support.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, and `tests/benchmarks/test_benchmark_manifest_validation.py` so they route those owner surfaces through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the shared-support ownership assertions stop treating the moved compile-owner surface as `benchmark_test_support`-owned and instead verify the tighter source-tree owner boundary.
- Keep the neutral compile-contract machinery shared unless a direct dependency forces a minimal adjustment:
  - `CompiledPatternModuleCompileContractCase`
  - `build_compiled_pattern_module_compile_contract_cases(...)`
  - `build_compiled_pattern_module_contract_anchor_lanes(...)`
  - `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
- Do not widen into pattern-boundary support, collection/replacement owner support, benchmark workload files, generated reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_contract'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES|_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS|_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES)\\b' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` had no blocked architecture task to reopen or normalize.
  - `rg -n 'RBR-1406\\b' ops/state/backlog.md ops/state/current_status.md ops/tasks ops/state/decision_log.md` returned no reserved or duplicate `RBR-1406`.
- Candidate selection in this run:
  - The first obvious post-JSON candidate was the source-tree report-contract route, but `RBR-1405` landed that cleanup already and the checkout now reflects its intended end state.
  - The next viable cross-file seam is the compiled-pattern module-compile owner surface: it still sits in shared benchmark support while source-tree owner suites and manifest-validation coverage consume it as a source-tree-specific route.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'` passed with `77 passed, 202 deselected in 1.62s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_contract'` passed with `7 passed, 57 deselected in 0.13s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_compile_standard_definition_surface_moves_to_shared_support or compiled_pattern_module_compile_standard_benchmark_definitions_are_shared_support_owned'` passed with `2 passed, 118 deselected in 0.15s`; those assertions should be rewritten by the implementation task as the owner boundary tightens.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
