## RBR-1437: Localize compile-proxy standard-definition layer onto benchmark meta-tests

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining compile-proxy standard-definition helper layer from `tests/benchmarks/benchmark_test_support.py` now that its real consumers are confined to `tests/benchmarks/test_benchmark_test_support.py`.
- The live probe in this run showed that the compile-proxy selector/signature helpers and their one-definition export are only referenced by the support module itself plus the benchmark-support meta-tests, so shared benchmark support is still carrying a whole support-meta-only layer.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers, while leaving the compile-manifest path constants in place because `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` still consumes `COMPILE_MATRIX_MANIFEST_PATH`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the compile-proxy standard-definition helper layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_benchmark_test_support.py` so shared support no longer exports:
  - `compile_proxy_correctness_case_signature(...)`
  - `compile_proxy_workload_signature(...)`
  - `is_compile_proxy_workload(...)`
  - `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` to own that layer locally instead of asserting against or importing it through `tests.benchmarks.benchmark_test_support`.
- Keep `COMPILE_MATRIX_MANIFEST_PATH` and `REGRESSION_MATRIX_MANIFEST_PATH` on `tests/benchmarks/benchmark_test_support.py`; they are not part of this cleanup because the live reference scan in this run still found a non-meta-test consumer for `COMPILE_MATRIX_MANIFEST_PATH` in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move shared helpers that still have real cross-suite consumers such as manifest loading, workload/result contract assertions, workload execution, payload freezing, or compile-manifest path constants

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compile_proxy'`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^((def (compile_proxy_correctness_case_signature|compile_proxy_workload_signature|is_compile_proxy_workload)\\b)|(COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS\\s*=))' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Completed 2026-03-27: removed the compile-proxy selector/signature/definition layer from `tests/benchmarks/benchmark_test_support.py`, redefined that layer locally inside `tests/benchmarks/test_benchmark_test_support.py` against the shared compile-manifest path constants, and verified the scoped pytest target, `py_compile`, and the negative `rg` export check all pass.
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1437|RBR-1438|RBR-1439" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside completed task notes, so `RBR-1437` was available.
- Candidate selection in this run:
  - `rg -n "compile_proxy_correctness_case_signature|compile_proxy_workload_signature|is_compile_proxy_workload|COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS" tests/benchmarks -g '*.py'` showed the compile-proxy helper family defined in shared support and otherwise referenced only by `tests/benchmarks/test_benchmark_test_support.py`.
  - `rg -n "COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH" tests/benchmarks -g '*.py'` showed `COMPILE_MATRIX_MANIFEST_PATH` is still consumed by `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the manifest-path constants themselves are not safe to move in this task.
  - `bash -lc "! rg -n '^((def (compile_proxy_correctness_case_signature|compile_proxy_workload_signature|is_compile_proxy_workload)\\b)|(COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS\\s*=))' tests/benchmarks/benchmark_test_support.py"` is currently red because the compile-proxy helper layer still lives in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compile_proxy'` passed with `6 passed, 194 deselected in 0.18s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py` passed.
