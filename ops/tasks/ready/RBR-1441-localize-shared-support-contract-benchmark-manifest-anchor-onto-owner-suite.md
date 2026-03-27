## RBR-1441: Localize shared-support contract benchmark manifest anchor onto owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining cross-suite benchmark-support dependency from `tests/python/test_shared_test_support_contract.py` now that `tests/benchmarks/benchmark_test_support.py` no longer owns benchmark manifest-path constants.
- Keep the generic shared-support contract suite self-contained by defining the benchmark manifest anchor it uses locally instead of routing that path through benchmark-specific shared support.

## Deliverables
- `tests/python/test_shared_test_support_contract.py`

## Acceptance Criteria
- Rewrite `tests/python/test_shared_test_support_contract.py` so it no longer imports `COMPILE_MATRIX_MANIFEST_PATH` from `tests.benchmarks.benchmark_test_support`.
- Define the compile-matrix manifest path inside `tests/python/test_shared_test_support_contract.py` next to the other owner-local manifest anchors and keep the existing benchmark scorecard assertions pointed at that local constant.
- Keep the run bounded to that boundary cleanup:
  - do not reintroduce benchmark manifest-path constants into `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/python/test_shared_test_support_contract.py -q`
- `./.venv/bin/python -m py_compile tests/python/test_shared_test_support_contract.py tests/conftest.py`
- `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import COMPILE_MATRIX_MANIFEST_PATH$' tests/python/test_shared_test_support_contract.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1441|RBR-1442|RBR-1443|RBR-1444|RBR-1445" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1441` was available.
- Candidate selection in this run:
  - A live reference scan showed the only remaining import of `COMPILE_MATRIX_MANIFEST_PATH` from `tests.benchmarks.benchmark_test_support` is in `tests/python/test_shared_test_support_contract.py`.
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` and `tests/benchmarks/test_benchmark_test_support.py` already define their own manifest-path constants locally, so the remaining cleanup is a single cross-suite boundary fix rather than another shared-support export change.
  - The failing collection in `tests/python/test_shared_test_support_contract.py` is a direct consequence of the intended cleanup from `RBR-1440`: the suite still imports a constant that shared support no longer exports.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/python/test_shared_test_support_contract.py -q` failed during collection with `ImportError: cannot import name 'COMPILE_MATRIX_MANIFEST_PATH' from 'tests.benchmarks.benchmark_test_support'`; that red state belongs to the exact cleanup this task queues.
  - `./.venv/bin/python -m py_compile tests/python/test_shared_test_support_contract.py tests/conftest.py` succeeded.
  - `bash -lc "! rg -n '^from tests\\.benchmarks\\.benchmark_test_support import COMPILE_MATRIX_MANIFEST_PATH$' tests/python/test_shared_test_support_contract.py"` is currently red because that exact import still exists in the owner suite.
