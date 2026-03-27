## RBR-1436: Move compiled-pattern module-compile owner helpers out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining compiled-pattern module-compile owner helper layer from `tests/benchmarks/benchmark_test_support.py` now that its real owner use is confined to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The live probe in this run showed that the compiled-pattern module-compile selector/signature helpers below are still defined in shared support, while the only non-meta-test call sites live on the source-tree combined owner suite.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers, and let the source-tree combined owner suite own its compiled-pattern module-compile contract selection/signature plumbing directly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move or inline the compiled-pattern module-compile owner helper layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so shared support no longer exports:
  - `_compiled_pattern_module_compile_keyword_kwargs_signature(...)`
  - `_module_workflow_compiled_pattern_compile_correctness_case_signature(...)`
  - `_module_workflow_compiled_pattern_compile_workload_signature(...)`
  - `_is_module_workflow_compiled_pattern_compile_workload(...)`
  - `_is_module_workflow_compiled_pattern_compile_success_workload(...)`
  - `_workload_matches_expected_exception(...)`
  - `_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(...)`
  - `_module_workflow_compiled_pattern_compile_keyword_workload_signature(...)`
  - `_is_module_workflow_compiled_pattern_compile_keyword_workload(...)`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to own that helper family locally instead of routing it through `tests.benchmarks.benchmark_test_support`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so its ownership assertions expect the compiled-pattern module-compile helper layer to live on the source-tree combined owner suite rather than in shared support.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move helpers that still have real cross-suite consumers such as workload loading, CPython workload execution, anchor/contract classes, or manifest/workload contract helpers outside this exact layer

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_compile or source_tree_combined_suite_owns_compile_contract_round_trip_helper'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def (_compiled_pattern_module_compile_keyword_kwargs_signature|_module_workflow_compiled_pattern_compile_correctness_case_signature|_module_workflow_compiled_pattern_compile_workload_signature|_is_module_workflow_compiled_pattern_compile_workload|_is_module_workflow_compiled_pattern_compile_success_workload|_workload_matches_expected_exception|_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature|_module_workflow_compiled_pattern_compile_keyword_workload_signature|_is_module_workflow_compiled_pattern_compile_keyword_workload)\\b' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Completed 2026-03-27: moved the compiled-pattern module-compile selector/signature helper family out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, updated the benchmark-support ownership assertions to expect local source-tree ownership, and verified the scoped pytest targets, `py_compile`, and the negative `rg` export check all pass.
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short --branch` showed a clean `main...origin/main` checkout in this run, so the runtime JSON count was not stale.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1436|RBR-1437|RBR-1438" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned no reserved or existing future use of `RBR-1436`.
- Candidate selection in this run:
  - `rg -n "_compiled_pattern_module_compile_keyword_kwargs_signature|_module_workflow_compiled_pattern_compile_correctness_case_signature|_module_workflow_compiled_pattern_compile_workload_signature|_is_module_workflow_compiled_pattern_compile_workload|_is_module_workflow_compiled_pattern_compile_success_workload|_workload_matches_expected_exception|_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature|_module_workflow_compiled_pattern_compile_keyword_workload_signature|_is_module_workflow_compiled_pattern_compile_keyword_workload|COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS" tests/benchmarks -g '*.py'` showed the helper family defined in shared support, referenced by the benchmark support meta-tests, and otherwise consumed by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`, so the remaining shared layer is specifically the compile helper family listed above rather than the standard-definition tuple itself.
  - The final `rg` command in Verification is currently red because those helper definitions still live in `tests/benchmarks/benchmark_test_support.py`; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_compile or source_tree_combined_suite_owns_compile_contract_round_trip_helper'` passed with `7 passed, 193 deselected in 0.34s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'` passed with `89 passed, 218 deselected in 1.66s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
