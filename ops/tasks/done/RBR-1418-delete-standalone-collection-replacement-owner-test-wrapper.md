## RBR-1418: Delete the standalone collection-replacement owner test wrapper

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the dedicated `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` layer now that the collection/replacement owner surface already lives on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- The remaining standalone suite is another benchmark-owner test wrapper around the surviving source-tree owner module, which keeps one more import path, consumer-module guard target, and owner-specific test file alive than the checkout needs.
- Fold the still-useful collection/replacement assertions into the surviving source-tree benchmark suites so the benchmark tests carry one fewer owner-wrapper module.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` (delete)
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Move the still-needed collection/replacement owner assertions onto `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and, only where the combined benchmark publication boundary is the natural home, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, preserving the current behavioral coverage for:
  - collection/replacement wrong-text-model owner metadata and contract-shape checks
  - positional-indexlike and keyword selector/signature coverage
  - collection/replacement manifest measured-row ownership checks
  - source-tree combined owner-alias routing and collection-replacement representative-workload assertions
  - source-tree contract workload/manifest helper coverage that currently only lives in the wrapper suite
- Update `tests/benchmarks/test_benchmark_test_support.py` so it no longer treats `tests.benchmarks.test_collection_replacement_benchmark_anchor_support` as a live consumer module, and keep or add a deleted-module assertion that the removed wrapper stays absent and unimportable.
- Remove live references to `tests.benchmarks.test_collection_replacement_benchmark_anchor_support` from the files listed above.
- Keep this task bounded to the redundant owner-test wrapper deletion; do not reopen `source_tree_benchmark_anchor_support.py` support-surface rewrites, `benchmark_test_support.py` decomposition, benchmark manifest edits, or report/status updates.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py -q`
- `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc '! test -e tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1418|RBR-1419|RBR-1420" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks` found no reserved future-id use for `RBR-1418`; the only hits were historical notes inside completed `RBR-1416` and `RBR-1417` task files.
- Candidate selection in this run:
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still imports `tests.benchmarks.source_tree_benchmark_anchor_support as support`, so the wrapper suite no longer owns a distinct benchmark-support module.
  - `rg -n "tests\\.benchmarks\\.test_collection_replacement_benchmark_anchor_support|test_collection_replacement_benchmark_anchor_support" tests/benchmarks ops/tasks ops/state` found live code references only in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_test_support.py`.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already aliases `collection_replacement_support = source_tree_owner_support`, which confirms the combined benchmark publication lane has already collapsed onto the source-tree owner path.
  - I stopped after this first viable post-JSON candidate because it removes one whole owner-test wrapper file instead of widening into another local helper-by-helper cleanup.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `620 passed, 1557 subtests passed in 13.82s`.
  - `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed.
  - `bash -lc '! test -e tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'` currently fails only because the redundant wrapper file still exists, which is the exact cleanup this task queues.

## Completion
- Moved the surviving collection/replacement owner assertions into `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including wrong-text-model contract coverage, positional-indexlike selector/signature checks, measured-row ownership checks, and combined conditional slice ownership assertions.
- Updated `tests/benchmarks/test_benchmark_test_support.py` to stop treating `tests.benchmarks.test_collection_replacement_benchmark_anchor_support` as a live consumer module and to keep the deleted wrapper unimportable.
- Deleted `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`.
- Verification in this completion run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `646 passed, 1573 subtests passed in 14.62s`.
  - `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed.
  - `bash -lc '! test -e tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py'` passed.
