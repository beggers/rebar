## RBR-1421: Delete the standalone source-tree benchmark anchor support layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove `tests/benchmarks/source_tree_benchmark_anchor_support.py` now that it has become a standalone owner-support layer for one surviving suite plus its own dedicated contract test file.
- Leave the benchmark test stack with one fewer bespoke support module after the JSON burn-down by pushing genuinely shared helpers into `tests/benchmarks/benchmark_test_support.py` and keeping suite-local scorecard/contract shaping inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Delete the matching dedicated support-suite file `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` instead of preserving a second benchmark-owner contract lane for a module that no longer needs to exist.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Delete `tests/benchmarks/source_tree_benchmark_anchor_support.py` entirely.
- Delete `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` entirely, folding any still-useful shared-surface or routing assertions into `tests/benchmarks/test_benchmark_test_support.py` and keeping suite-local behavior checks with `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it no longer imports `source_tree_benchmark_anchor_support`; any helpers that remain genuinely shared across benchmark tests should come from `tests/benchmarks/benchmark_test_support.py`, and any source-tree-combined-only shaping should stay local to the combined suite.
- Update `tests/benchmarks/benchmark_test_support.py` and `tests/benchmarks/test_benchmark_test_support.py` so cache clearing, import-routing checks, and support-surface assertions no longer mention the deleted module or deleted dedicated test suite.
- Keep the task bounded to deleting that standalone support/test layer; do not reopen benchmark workload manifests, `python/rebar_harness/benchmarks.py`, reporting/status files, or unrelated benchmark-owner simplifications.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! test -e tests/benchmarks/source_tree_benchmark_anchor_support.py && ! test -e tests/benchmarks/test_source_tree_benchmark_anchor_support.py && ! rg -n 'source_tree_benchmark_anchor_support|test_source_tree_benchmark_anchor_support' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1421|RBR-1422|RBR-1423|RBR-1424" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1421` was not reserved by planning-owned frontier notes.
- Why this target:
  - `rg -n "source_tree_benchmark_anchor_support" tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the module is still imported directly only by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, while the rest of the references are cache-clearing and contract assertions inside shared benchmark-test support.
  - The current benchmark stack still carries a dedicated module plus a dedicated test file for that single owner-support surface even after `RBR-1419` and `RBR-1420` removed its manifest-validation and scorecard wrapper layers.
  - That makes this the next bounded post-JSON structural deletion with a clear cross-file payoff: one benchmark support module and one benchmark test file can disappear together without reopening feature behavior or manifest data.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `671 passed, 1573 subtests passed in 14.16s`.
  - `python3 -m py_compile tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n 'source_tree_benchmark_anchor_support' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py | wc -l"` returned `67`, confirming the remaining coupling is concentrated in this support/test layer rather than spread across the wider repo.
