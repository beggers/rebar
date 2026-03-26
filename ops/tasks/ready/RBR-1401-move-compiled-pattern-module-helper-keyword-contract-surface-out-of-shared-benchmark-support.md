## RBR-1401: Move the compiled-pattern module-helper keyword contract surface out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining collection-replacement-owned compiled-pattern module-helper keyword contract surface from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still defines `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_*` contract specs, workload selections, and surface params even though the workload selectors and keyword-shape logic for that lane already live in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Move that one contract surface onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so shared benchmark support stops owning a collection-replacement-only lane and keeps only the genuinely shared compiled-pattern helper machinery.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS`, `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS`, and `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate that contract surface on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, wired directly to the existing owner-local helpers `_collection_replacement_keyword_parameter_name(...)`, `_collection_replacement_positional_keyword_field(...)`, `_is_collection_replacement_compiled_pattern_module_helper_keyword_workload(...)`, and `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` instead of routing collection-replacement ownership back through shared support.
- Keep any genuinely shared primitives that this contract surface still needs in `tests/benchmarks/benchmark_test_support.py`; do not widen into moving `RecordingBenchmarkModule`, `compiled_pattern_contract_expected_build_calls(...)`, or other shared compiled-pattern support in the same run.
- Update the ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` so this keyword-contract lane is no longer treated as shared-support-owned, and update the combined-suite and manifest-validation tests to consume the moved surface from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without changing benchmark workloads, contract payloads, or scorecard behavior.
- Keep the run bounded to this one owner-boundary cleanup; do not also move the collection-replacement wrong-text-model lane, source-tree contract builders, or pattern-boundary helpers.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_helper_keyword'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_(CONTRACT_SPEC|ERROR_CONTRACT_SPEC|SOURCE_WORKLOADS|PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|ERROR_SOURCE_WORKLOADS|CONTRACT_SURFACES|CONTRACT_SURFACE_PARAMS|CONTRACT_SOURCE_WORKLOAD_PARAMS|PRECOMPILE_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer moving the existing owner-local contract surface onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` over adding another neutral helper module, registry, or wrapper layer.
- Do not change benchmark workload files, generated reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1401' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1401`.
- Candidate selection in this run:
  - With both tracked and live JSON counts at zero, I inspected the remaining benchmark-support layers under `tests/benchmarks/`.
  - `tests/benchmarks/benchmark_test_support.py` is still a 4834-line shared file, and `bash -lc "rg -n '_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_(CONTRACT_SPEC|ERROR_CONTRACT_SPEC|SOURCE_WORKLOADS|PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|ERROR_SOURCE_WORKLOADS|CONTRACT_SURFACES|CONTRACT_SURFACE_PARAMS|CONTRACT_SOURCE_WORKLOAD_PARAMS|PRECOMPILE_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"` shows the collection-replacement-only keyword contract surface is still owned there.
  - `tests/benchmarks/test_benchmark_test_support.py` still contains `test_compiled_pattern_module_helper_keyword_shared_surface_stays_shared_support_owned`, which is the exact ownership assertion this cleanup should flip.
  - This is a bounded cross-file simplification because it removes one remaining owner-specific layer from shared support without widening into broader benchmark-helper rewrites.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_helper_keyword'` passed with `2 passed, 176 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` passed with `66 passed, 213 deselected in 0.41s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword'` passed with `4 passed, 60 deselected in 0.19s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_(CONTRACT_SPEC|ERROR_CONTRACT_SPEC|SOURCE_WORKLOADS|PRECOMPILE_ANCHOR_SOURCE_WORKLOADS|ERROR_SOURCE_WORKLOADS|CONTRACT_SURFACES|CONTRACT_SURFACE_PARAMS|CONTRACT_SOURCE_WORKLOAD_PARAMS|PRECOMPILE_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"` currently fails only because the exact shared-support ownership this task should remove is still present.
