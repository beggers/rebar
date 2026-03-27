## RBR-1446: Delete benchmark-test-support shared layer

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove `tests/benchmarks/benchmark_test_support.py` now that it only carries a tiny manifest-helper layer while a dedicated `tests/benchmarks/test_benchmark_test_support.py` meta-suite still exists to police it.
- Move the remaining owner-specific helper behavior onto the benchmark suites that actually consume it so the benchmark tests read directly through ordinary local helpers instead of a bespoke shared support module plus a second contract file.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Rewrite `tests/benchmarks/test_benchmark_manifest_validation.py` so it no longer imports `tests.benchmarks.benchmark_test_support`, and instead defines the temporary-manifest writer it needs locally.
- Rewrite `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it no longer imports `tests.benchmarks.benchmark_test_support`, and instead defines the temporary-manifest and live-workload helper surface it needs locally.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it no longer imports `tests.benchmarks.benchmark_test_support`, and instead owns its manifest/workload selection helpers locally while continuing to use direct `rebar_harness.benchmarks` imports and `tests.conftest.run_harness_scorecard`.
- Update `tests/python/test_shared_test_support_contract.py` only as needed so it stops asserting import structure around the deleted `tests.benchmarks.benchmark_test_support` layer.
- Delete `tests/benchmarks/benchmark_test_support.py`.
- Delete `tests/benchmarks/test_benchmark_test_support.py`.
- Keep the run bounded to this shared-layer deletion:
  - do not change benchmark workload definitions under `benchmarks/workloads/`
  - do not change `python/rebar_harness/benchmarks.py`, `tests/conftest.py`, or runtime/reporting code
  - do not add a replacement shared support module

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
- `./.venv/bin/python -m py_compile tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
- `bash -lc "! rg -n 'benchmark_test_support' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py tests/benchmarks"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1446|RBR-1447|RBR-1448" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1446` was available.
- Candidate selection in this run:
  - `rg -n "from tests\\.benchmarks import benchmark_test_support|import tests\\.benchmarks\\.benchmark_test_support|benchmark_test_support\\." tests` showed live functional imports only in `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, plus the dedicated meta-contract file and one shared-support contract assertion.
  - `tests/benchmarks/benchmark_test_support.py` is only 57 lines, while `tests/benchmarks/test_benchmark_test_support.py` is 6743 lines; the remaining support layer is now structurally more expensive to police than to inline onto the benchmark owner suites.
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` confirmed the shared module now exports only `load_manifest`, `manifest_workloads`, `live_manifest_workload`, `live_manifest_workloads`, and `_write_test_manifest`; it does not own a broader reusable benchmark API anymore.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py -q` passed (`771 passed, 3 skipped, 1573 subtests passed`).
  - The negative `rg` verification is intentionally red in the current checkout because the shared layer and its contract file still exist and are the target of this task.

## Completion
- Completed 2026-03-27.
- Inlined the temporary manifest writer into `tests/benchmarks/test_benchmark_manifest_validation.py`.
- Inlined manifest/workload selection plus temporary-manifest helpers into `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keeping direct `rebar_harness.benchmarks` imports and `tests.conftest.run_harness_scorecard`.
- Updated `tests/python/test_shared_test_support_contract.py` to stop asserting the deleted benchmark shared-layer import structure.
- Deleted `tests/benchmarks/benchmark_test_support.py` and `tests/benchmarks/test_benchmark_test_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
  - `./.venv/bin/python -m py_compile tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py`
  - `bash -lc "! rg -n 'benchmark_test_support' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_shared_test_support_contract.py tests/benchmarks"`
