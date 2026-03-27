## RBR-1439: Localize source-tree-combined selection and recording helper layer onto owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining source-tree-combined-only workload-selection, recording-module, and manifest-constant layer from `tests/benchmarks/benchmark_test_support.py` now that its live consumers are confined to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the benchmark-support meta-tests.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers that still serve multiple suites, especially the publication-runtime contracts and the support module's own shared cache/workload helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the remaining source-tree-combined-only helper family out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so shared support no longer exports:
  - `RecordingBenchmarkCompiledPattern`
  - `RecordingBenchmarkModule`
  - `selected_manifest_workloads(...)`
  - `freeze_signature_value(...)`
  - `AnchoredWorkloadCasePair`
  - `COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS`
  - `COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS`
  - `MODULE_BOUNDARY_MANIFEST_PATH`
  - `OPTIONAL_GROUP_MANIFEST_PATH`
  - `NESTED_GROUP_MANIFEST_PATH`
  - `EXACT_REPEAT_MANIFEST_PATH`
  - `RANGED_REPEAT_MANIFEST_PATH`
  - `GROUPED_ALTERNATION_MANIFEST_PATH`
  - `GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH`
  - `NESTED_GROUP_REPLACEMENT_MANIFEST_PATH`
  - `OPEN_ENDED_MANIFEST_PATH`
  - `COLLECTION_REPLACEMENT_MANIFEST_PATH`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to call and patch that layer locally instead of routing through `tests.benchmarks.benchmark_test_support`.
- Extend `tests/benchmarks/test_benchmark_test_support.py` so the meta-tests assert that this selection/recording/helper-constant surface now belongs to the source-tree-combined owner suite and no longer appears on shared benchmark support.
- Keep the run bounded to that ownership cleanup:
  - do not move `manifest_workloads(...)`, `live_manifest_workload(...)`, `live_manifest_workloads(...)`, `run_benchmark_workload_with_cpython(...)`, or `assert_benchmark_workload_matches_expected_result(...)`; those still have multi-suite consumers
  - do not move `COMPILE_MATRIX_MANIFEST_PATH`, `CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH`, or `NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH`; `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still consumes that publication-runtime path layer
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(class (RecordingBenchmarkCompiledPattern|RecordingBenchmarkModule|AnchoredWorkloadCasePair)\\b|def (selected_manifest_workloads|freeze_signature_value)\\b|(MODULE_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH|COLLECTION_REPLACEMENT_MANIFEST_PATH|COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS)\\s*=)' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1439|RBR-1440|RBR-1441|RBR-1442" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1439` was available.
- Candidate selection in this run:
  - A live AST/reference scan across `tests/benchmarks/*.py` showed the symbol family listed above is only consumed outside `tests/benchmarks/benchmark_test_support.py` by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus `tests/benchmarks/test_benchmark_test_support.py`.
  - The same scan showed `run_benchmark_workload_with_cpython(...)`, `assert_benchmark_workload_matches_expected_result(...)`, `live_manifest_workload(...)`, and `live_manifest_workloads(...)` still have both source-tree-combined and publication-runtime consumers, so they are intentionally out of scope.
  - `bash -lc "! rg -n '^(class (RecordingBenchmarkCompiledPattern|RecordingBenchmarkModule|AnchoredWorkloadCasePair)\\b|def (selected_manifest_workloads|freeze_signature_value)\\b|(MODULE_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH|COLLECTION_REPLACEMENT_MANIFEST_PATH|COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS|COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS)\\s*=)' tests/benchmarks/benchmark_test_support.py"` is currently red because that owner-only layer still lives in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q` passed with `203 passed in 0.68s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q` passed with `307 passed, 1573 subtests passed in 12.83s`.
