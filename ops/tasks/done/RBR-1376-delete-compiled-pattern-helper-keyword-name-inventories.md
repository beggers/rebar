## RBR-1376: Delete compiled-pattern helper keyword name inventories

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the bookkeeping-only compiled-pattern helper keyword name inventories from the benchmark-support test modules, and rewrite the affected ownership assertions to use direct targeted checks instead of mirrored module-level name sets.

## Deliverables
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete these bookkeeping inventories without moving them sideways or replacing them with another mirrored exported set:
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SHARED_SURFACE_NAMES` from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_COMBINED_SUITE_OWNER_NAMES` from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SHARED_SURFACE_NAMES` from `tests/benchmarks/test_benchmark_test_support.py`
- Rewrite the affected assertions in those two files so they preserve the same owner boundaries through direct targeted checks rather than through shared bookkeeping inventories. Preserve these boundaries explicitly:
  - the source-tree support module still does not define or export the compiled-pattern helper keyword surfaces that belong on `tests.benchmarks.benchmark_test_support`;
  - the combined source-tree benchmark suite still reaches the exact compiled-pattern helper keyword owner names through the `benchmark_test_support` alias path rather than through direct `from ... import ...` imports, local aliases, or `source_tree_benchmark_anchor_support` attribute loads;
  - `tests.benchmarks.benchmark_test_support` still exports the exact compiled-pattern helper keyword support names that the ownership tests are proving.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n 'COMPILED_PATTERN_MODULE_HELPER_KEYWORD_(SHARED_SURFACE_NAMES|COMBINED_SUITE_OWNER_NAMES)\\s*=' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting the mirrored name inventories over recreating them under new names, moving them into another helper module, or replacing them with another shared registry.
- Keep the run bounded to this compiled-pattern helper keyword ownership cleanup in the benchmark-support tests.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1376|RBR-1377|RBR-1378' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Post-JSON cleanup stayed in the benchmark-support ownership layer because tracked and live JSON counts are both zero.
  - `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SHARED_SURFACE_NAMES` is duplicated across `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_benchmark_test_support.py`, and `COMPILED_PATTERN_MODULE_HELPER_KEYWORD_COMBINED_SUITE_OWNER_NAMES` is a companion bookkeeping inventory in the source-tree support test.
  - Those inventories only feed ownership assertions inside the benchmark-support test modules; they do not drive runtime harness behavior or published benchmark selection.
  - The current green test slice already passes without any runtime consumer depending on those registries, which makes them a bounded structural cleanup target rather than live harness logic.
- Verification status in this planning run:
  - Completed in this run by deleting the three module-level bookkeeping inventories and rewriting the affected ownership checks in place with exact per-test assertions.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `277 passed in 1.86s`
  - `python3 -m py_compile tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n 'COMPILED_PATTERN_MODULE_HELPER_KEYWORD_(SHARED_SURFACE_NAMES|COMBINED_SUITE_OWNER_NAMES)\\s*=' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` now passes
