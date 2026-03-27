## RBR-1440: Localize benchmark manifest-path constants onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining benchmark manifest-path constant layer from `tests/benchmarks/benchmark_test_support.py` now that those constants no longer belong to genuinely shared benchmark support.
- Keep `tests/benchmarks/benchmark_test_support.py` limited to helpers that still serve multiple benchmark suites, while moving owner-specific manifest anchors next to the suites that actually consume them.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the remaining manifest-path constant layer out of `tests/benchmarks/benchmark_test_support.py` so shared support no longer exports:
  - `COMPILE_MATRIX_MANIFEST_PATH`
  - `REGRESSION_MATRIX_MANIFEST_PATH`
  - `CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH`
  - `NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH`
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it owns the manifest-path constants it actually uses instead of routing those paths through `tests.benchmarks.benchmark_test_support`.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so the compile-proxy definition layer and ownership assertions use suite-local manifest-path constants and assert that shared benchmark support no longer defines the constant layer above.
- Keep the run bounded to that ownership cleanup:
  - do not move `_write_test_manifest(...)`, `live_manifest_workloads(...)`, `run_benchmark_workload_with_cpython(...)`, or `assert_benchmark_workload_matches_expected_result(...)`; those still have multi-suite consumers
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_publication_runtime_contracts.py -q`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `bash -lc "! rg -n '^(COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH|CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH|NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH)\\s*=' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1440|RBR-1441|RBR-1442|RBR-1443|RBR-1444" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1440` was available.
- Candidate selection in this run:
  - A live reference scan across `tests/benchmarks/*.py` showed `COMPILE_MATRIX_MANIFEST_PATH`, `CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH`, and `NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH` are consumed outside `tests/benchmarks/benchmark_test_support.py` only by `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` plus `tests/benchmarks/test_benchmark_test_support.py`.
  - The same scan showed `REGRESSION_MATRIX_MANIFEST_PATH` is consumed outside shared support only by `tests/benchmarks/test_benchmark_test_support.py`, alongside the compile-proxy meta-definition layer that was already localized there.
  - `bash -lc "! rg -n '^(COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH|CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH|NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH)\\s*=' tests/benchmarks/benchmark_test_support.py"` is currently red because that owner-only constant layer still lives in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q` passed with `204 passed in 0.71s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_publication_runtime_contracts.py -q` passed with `192 passed, 3 skipped in 0.31s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` succeeded.

## Completion
- Landed the owner-local benchmark manifest-path cleanup by deleting the manifest-path constant layer from `tests/benchmarks/benchmark_test_support.py`, defining the compile/runtime manifest anchors inside the two consuming suites, and updating the ownership meta-tests to assert those constants stay local while shared helper exports remain shared.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -q` passed with `205 passed in 0.93s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_publication_runtime_contracts.py -q` passed with `192 passed, 3 skipped in 0.36s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` succeeded.
  - `bash -lc "! rg -n '^(COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH|CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH|NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH)\\s*=' tests/benchmarks/benchmark_test_support.py"` succeeded.
