## RBR-1434: Move the module-workflow keyword owner layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining module-workflow keyword owner layer from `tests/benchmarks/benchmark_test_support.py` now that it no longer has real cross-suite consumers.
- The live post-JSON probe in this run showed that the `_module_workflow_keyword_*` helper family, `_is_encoded_indexlike_payload(...)`, and `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` are defined in shared support, but the only non-meta-test owner usage is inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers, and let the source-tree combined owner suite own its module-workflow keyword selector/signature/definition plumbing directly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move or inline the module-workflow keyword owner layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so shared support no longer exports owner-only helpers:
  - `_is_encoded_indexlike_payload(...)`
  - `_module_workflow_keyword_correctness_case_signature(...)`
  - `_is_module_workflow_keyword_flags_workload(...)`
  - `_is_module_workflow_keyword_error_workload(...)`
  - `_module_workflow_keyword_workload_args(...)`
  - `_module_workflow_keyword_workload_signature(...)`
  - `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to own that layer locally instead of routing it through `tests.benchmarks.benchmark_test_support`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so its ownership assertions expect the module-workflow keyword layer to live on the source-tree combined owner suite rather than on shared support.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move helpers that still have real cross-suite consumers such as manifest loading, CPython workload execution, or ownership-boundary assertion helpers outside this exact layer

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'module_workflow_keyword or encoded_indexlike_payload or inline_standard_definition_exports_reuse_named_manifest_path_constants'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q --collect-only tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'def _is_encoded_indexlike_payload|def _module_workflow_keyword_correctness_case_signature|def _is_module_workflow_keyword_flags_workload|def _is_module_workflow_keyword_error_workload|def _module_workflow_keyword_workload_args|def _module_workflow_keyword_workload_signature|^MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS =' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -name 'RBR-1434*' -o -name 'RBR-1435*' -o -name 'RBR-1436*' | sort` returned no matches.
  - `rg -n "RBR-1434|RBR-1435|RBR-1436" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1434` was available.
- Candidate selection in this run:
  - The first post-JSON probe showed that `_is_encoded_indexlike_payload(...)`, the `_module_workflow_keyword_*` helper family, and `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` still live in `tests/benchmarks/benchmark_test_support.py`.
  - The same probe showed those names are only exercised by `tests/benchmarks/test_benchmark_test_support.py` and by the source-tree combined owner suite, with the only non-meta-test owner use being `benchmark_test_support._is_module_workflow_keyword_error_workload` inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `bash -lc "! rg -n 'def _is_encoded_indexlike_payload|def _module_workflow_keyword_correctness_case_signature|def _is_module_workflow_keyword_flags_workload|def _is_module_workflow_keyword_error_workload|def _module_workflow_keyword_workload_args|def _module_workflow_keyword_workload_signature|^MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS =' tests/benchmarks/benchmark_test_support.py"` is currently red because that owner-only layer still lives in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'module_workflow_keyword or encoded_indexlike_payload or inline_standard_definition_exports_reuse_named_manifest_path_constants'` passed with `3 passed, 197 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q --collect-only tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'` passed and collected the targeted source-tree owner tests.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
