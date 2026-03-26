## RBR-1374: Delete source-tree moved-name inventories

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the bookkeeping-only `SOURCE_TREE_*` moved-name and centralized-path inventories from `tests/benchmarks/source_tree_benchmark_anchor_support.py`, and delete the mirrored `_MOVED_SOURCE_TREE_*` / `_CENTRALIZED_SOURCE_TREE_*` inventories from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, so this owner boundary stops publishing and re-declaring name lists that exist only to drive support-contract assertions.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these exported bookkeeping inventories from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without moving them sideways or replacing them with another exported registry:
  - `SOURCE_TREE_MOVED_CLASS_NAMES`
  - `SOURCE_TREE_MOVED_FUNCTION_NAMES`
  - `SOURCE_TREE_MOVED_CONSTANT_NAMES`
  - `SOURCE_TREE_LOCAL_CONTRACT_BUILDER_CONSTANT_NAMES`
  - `SOURCE_TREE_CENTRALIZED_MANIFEST_PATH_NAMES`
- Delete the mirrored test-only inventories from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`:
  - `_MOVED_SOURCE_TREE_CLASS_NAMES`
  - `_MOVED_SOURCE_TREE_FUNCTION_NAMES`
  - `_MOVED_SOURCE_TREE_CONSTANT_NAMES`
  - `_LOCAL_SOURCE_TREE_CONTRACT_BUILDER_CONSTANT_NAMES`
  - `_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES`
- Rewrite the affected assertions in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to keep the same architectural boundary through direct targeted checks instead of shared inventory tuples. Preserve these boundaries explicitly:
  - the source-tree owner still defines the live combined-case classes/functions it actually owns locally;
  - the compiled-pattern module-compile and helper-keyword support surfaces remain owned by `tests.benchmarks.benchmark_test_support`, not by the source-tree owner;
  - the centralized manifest-path names continue to be read through `benchmark_test_support` rather than redefined locally on the source-tree owner or in the test module.
- Do not change benchmark manifests, workload selection, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^SOURCE_TREE_(MOVED_CLASS_NAMES|MOVED_FUNCTION_NAMES|MOVED_CONSTANT_NAMES|LOCAL_CONTRACT_BUILDER_CONSTANT_NAMES|CENTRALIZED_MANIFEST_PATH_NAMES)\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_CLASS_NAMES|_MOVED_SOURCE_TREE_FUNCTION_NAMES|_MOVED_SOURCE_TREE_CONSTANT_NAMES|_LOCAL_SOURCE_TREE_CONTRACT_BUILDER_CONSTANT_NAMES|_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES)\\s*=' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the inventories over recreating them under new names, moving them into another owner module, or replacing them with another mirrored test-only list.
- Keep the run bounded to this single source-tree benchmark-support inventory cleanup and the ownership assertions that currently depend on it.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1374|RBR-1375|RBR-1376|RBR-1377|RBR-1378|RBR-1379|RBR-1380' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - Post-JSON cleanup stayed in the benchmark-support ownership layer because tracked and live JSON counts are both zero.
  - `SOURCE_TREE_MOVED_CLASS_NAMES`, `SOURCE_TREE_MOVED_FUNCTION_NAMES`, `SOURCE_TREE_MOVED_CONSTANT_NAMES`, `SOURCE_TREE_LOCAL_CONTRACT_BUILDER_CONSTANT_NAMES`, and `SOURCE_TREE_CENTRALIZED_MANIFEST_PATH_NAMES` are defined only in `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
  - The mirrored `_MOVED_SOURCE_TREE_*`, `_LOCAL_SOURCE_TREE_CONTRACT_BUILDER_CONSTANT_NAMES`, and `_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES` lists are defined only in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`.
  - The current green support-contract suite already passes without any runtime consumer reading those inventories, which makes them a bounded bookkeeping-only cleanup target rather than live harness behavior.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed with `277 passed in 1.55s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n '^SOURCE_TREE_(MOVED_CLASS_NAMES|MOVED_FUNCTION_NAMES|MOVED_CONSTANT_NAMES|LOCAL_CONTRACT_BUILDER_CONSTANT_NAMES|CENTRALIZED_MANIFEST_PATH_NAMES)\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those exported bookkeeping inventories still exist, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_CLASS_NAMES|_MOVED_SOURCE_TREE_FUNCTION_NAMES|_MOVED_SOURCE_TREE_CONSTANT_NAMES|_LOCAL_SOURCE_TREE_CONTRACT_BUILDER_CONSTANT_NAMES|_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES)\\s*=' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the source-tree support-contract test still mirrors those inventories locally, and that failure belongs exactly to this cleanup
