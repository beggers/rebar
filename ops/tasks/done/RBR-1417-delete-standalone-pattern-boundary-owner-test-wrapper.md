## RBR-1417: Delete the standalone pattern-boundary owner test wrapper

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the dedicated `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` layer now that the actual pattern-boundary owner module was already folded into `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- The remaining standalone suite is now only a test wrapper around `source_tree_benchmark_anchor_support`, which keeps one more benchmark-owner import path, alias surface, and consumer-module guard target alive than the checkout needs.
- Fold the still-useful assertions into the surviving source-tree owner suite so the benchmark tests carry one fewer owner-specific wrapper file.

## Deliverables
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` (delete)
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`.
- Move the still-needed pattern-boundary owner assertions onto `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` or another already-live source-tree benchmark owner suite, preserving the current behavioral coverage for:
  - pattern-boundary standard-definition ownership and inventory reuse
  - pattern-window positional and keyword signature coverage
  - bounded-wildcard and verbose-regression selector/signature coverage
  - wrong-text-model contract-spec, manifest, payload, and runtime checks
- Update `tests/benchmarks/test_benchmark_test_support.py` so it no longer treats `tests.benchmarks.test_pattern_boundary_benchmark_anchor_support` as a live consumer module, and add a deleted-module assertion that the removed wrapper stays absent and unimportable.
- Remove live references to `tests.benchmarks.test_pattern_boundary_benchmark_anchor_support` from the files listed above.
- Keep this task bounded to the redundant owner-test wrapper deletion; do not reopen collection-replacement test-suite consolidation, shared `benchmark_test_support.py` decomposition, benchmark manifest edits, or report/status updates.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q`
- `python3 -m py_compile tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc '! test -e tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py'`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1417|RBR-1418|RBR-1419" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks` found no reserved future-id use for `RBR-1417`; the only hits were historical notes inside completed `RBR-1415` and `RBR-1416` task files.
- Candidate selection in this run:
  - I first checked whether another shared-support deletion inside `tests/benchmarks/benchmark_test_support.py` was ready, but that module is still the shared substrate for multiple benchmark suites and would have been too wide for one worker run.
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` is now a pure wrapper around `tests/benchmarks/source_tree_benchmark_anchor_support.py`; `rg -n "tests\\.benchmarks\\.test_pattern_boundary_benchmark_anchor_support|test_pattern_boundary_benchmark_anchor_support" tests/benchmarks ops/tasks ops/state` only found live code references in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_test_support.py`.
  - I stopped after this second bounded candidate because it removes one whole owner-test wrapper layer instead of widening into a larger shared-support rewrite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `342 passed in 1.35s`.
  - `python3 -m py_compile tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed.
  - `bash -lc '! test -e tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py'` currently fails only because the redundant wrapper file still exists, which is the exact cleanup this task queues.

## Completion
- Folded the pattern-boundary wrapper assertions into `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and deleted `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`.
- Updated `tests/benchmarks/test_benchmark_test_support.py` so the deleted wrapper is no longer treated as a live consumer module, while the deleted-module guard now asserts that `tests.benchmarks.test_pattern_boundary_benchmark_anchor_support` and its file stay absent.
- Verified the landed state with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q` -> `340 passed in 1.58s`
  - `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
  - `bash -lc '! test -e tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py'`
  - `git diff --name-status -- tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` -> `D`
