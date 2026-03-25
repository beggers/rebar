Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the redundant `tests/benchmarks/compile_proxy_benchmark_support.py` owner module by folding its small remaining surface onto `tests/benchmarks/benchmark_test_support.py`, so the benchmark-support layer stops carrying a dedicated file whose only real job is packaging compile-proxy manifest constants and one standard-definition tuple around helpers that already live in the shared support module.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- delete `tests/benchmarks/compile_proxy_benchmark_support.py`
- delete `tests/benchmarks/test_compile_proxy_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/benchmark_test_support.py` so it directly owns the full compile-proxy definition surface currently isolated in `tests/benchmarks/compile_proxy_benchmark_support.py`:
  - `COMPILE_MATRIX_MANIFEST_PATH`
  - `REGRESSION_MATRIX_MANIFEST_PATH`
  - `_build_compile_proxy_standard_benchmark_definitions()`
  - `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`
- Update the remaining import sites that still depend on `tests.benchmarks.compile_proxy_benchmark_support` so they import the compile-proxy manifest constants and standard-definition tuple from `tests.benchmarks.benchmark_test_support` instead. This includes:
  - `tests/benchmarks/standard_benchmark_anchor_support.py`
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py`
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- Delete `tests/benchmarks/compile_proxy_benchmark_support.py` once nothing in `tests/benchmarks/` imports it anymore.
- Delete `tests/benchmarks/test_compile_proxy_benchmark_support.py` and move any non-wrapper-specific assertions it still provides onto `tests/benchmarks/test_benchmark_test_support.py` and/or `tests/benchmarks/test_standard_benchmark_anchor_support.py`. Do not keep a replacement identity test whose only purpose is proving one module re-exports another.
- Preserve the current compile-proxy contract shape:
  - the manifest order must stay `(COMPILE_MATRIX_MANIFEST_PATH, REGRESSION_MATRIX_MANIFEST_PATH)`;
  - the anchor mapping for the single `compile-proxy` definition must stay byte-for-byte identical to the current expectations; and
  - the resulting definition must still reuse `is_compile_proxy_workload`, `compile_proxy_correctness_case_signature`, and `compile_proxy_workload_signature` from `tests/benchmarks/benchmark_test_support.py`.
- Do not add a new broker module. The point of this task is to remove one layer, not move it under another filename.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `bash -lc "test ! -e tests/benchmarks/compile_proxy_benchmark_support.py && test ! -e tests/benchmarks/test_compile_proxy_benchmark_support.py && ! rg -n 'compile_proxy_benchmark_support' tests/benchmarks"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark-support/test layer above. Do not widen it into benchmark manifests, harness runner behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Preserve the compile-proxy definition name, workload selection rules, manifest ordering, and anchor expectations exactly as they exist in the live checkout.
- Do not replace the deleted module with another one-file forwarding layer or a lazy proxy object elsewhere.

## Notes
- `RBR-1297` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1297|RBR-1298|RBR-1299|RBR-1300" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1297`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The simplification target is still concrete in the live checkout:
  - `tests/benchmarks/compile_proxy_benchmark_support.py` is `90` lines long and defines only two manifest-path constants, one cached builder, and a lazy `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` export around compile-proxy helpers that already live in `tests/benchmarks/benchmark_test_support.py`;
  - `rg -n "compile_proxy_benchmark_support" tests/benchmarks -g '*.py'` currently reports only four live import sites: `tests/benchmarks/standard_benchmark_anchor_support.py`, `tests/benchmarks/test_standard_benchmark_anchor_support.py`, `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, and `tests/benchmarks/test_compile_proxy_benchmark_support.py`; and
  - the dedicated test file is wrapper-focused coverage for that tiny owner module rather than a broader benchmark-harness behavior boundary.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed with `458 passed, 3 skipped in 0.65s`;
  - `bash -lc "test ! -e tests/benchmarks/compile_proxy_benchmark_support.py && test ! -e tests/benchmarks/test_compile_proxy_benchmark_support.py && ! rg -n 'compile_proxy_benchmark_support' tests/benchmarks"` currently fails because the module, its dedicated test, and live imports are still present; that failure belongs to the exact cleanup this task is queuing.
