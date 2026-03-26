## RBR-1373: Delete source-tree retired shared support registry

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the bookkeeping-only `SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES` export from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the source-tree owner module stops publishing a retired-name registry that exists only to satisfy ownership assertions and does not participate in live benchmark behavior.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete `SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it no longer reads `SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES` and instead keeps the same architectural boundary through direct targeted checks:
  - the compiled-pattern helper-keyword shared surface remains absent from `tests.benchmarks.source_tree_benchmark_anchor_support` and present on `tests.benchmarks.benchmark_test_support`;
  - the compiled-pattern module-compile standard-definition helpers remain absent from `tests.benchmarks.source_tree_benchmark_anchor_support` and present on `tests.benchmarks.benchmark_test_support`; and
  - the one collection-owned routed name this file still cares about remains owned by `tests.benchmarks.collection_replacement_benchmark_anchor_support`, not by the source-tree owner.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it no longer requires the helper-keyword shared surface names to stay listed inside a source-tree exported retired-name registry, while preserving the ownership check that those names stay on `tests.benchmarks.benchmark_test_support` and off the source-tree owner module.
- Do not add a replacement retired-name registry, compatibility alias, or another exported bookkeeping constant elsewhere.
- Keep the cleanup structural only; do not change benchmark workload data, benchmark execution behavior, scorecard logic, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting the registry over moving it sideways or recreating it under another module.
- Keep the run bounded to this single exported-registry cleanup and the ownership assertions that currently depend on it.

## Completion Notes
- Deleted `SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES` from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without adding a replacement registry.
- Reworked `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to keep the same ownership boundary through direct checks that:
  - compiled-pattern helper-keyword shared-surface names stay on `tests.benchmarks.benchmark_test_support` and off the source-tree owner;
  - compiled-pattern module-compile standard-definition helpers stay on `tests.benchmarks.benchmark_test_support` and off the source-tree owner; and
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS` stays collection-owned and absent from the source-tree owner.
- Reworked `tests/benchmarks/test_benchmark_test_support.py` so the helper-keyword shared-surface ownership check no longer depends on a source-tree retired-name registry.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `277 passed in 1.89s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"` passed
  - `bash -lc "! rg -n 'SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` passed

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1373|RBR-1374|RBR-1375' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Post-JSON cleanup stayed in the benchmark-support ownership layer because the live and tracked JSON counts are both zero.
  - `SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES` is defined only in `tests/benchmarks/source_tree_benchmark_anchor_support.py` and referenced only by `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` plus `tests/benchmarks/test_benchmark_test_support.py`, so it remains a bounded bookkeeping-only export rather than runtime support surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `276 passed in 1.54s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because the exported registry constant still exists, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py"` currently fails because the benchmark-support ownership tests still depend on that registry, and that failure belongs exactly to this cleanup
