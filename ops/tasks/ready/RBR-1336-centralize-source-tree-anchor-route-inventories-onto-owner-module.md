## RBR-1336: Centralize source-tree anchor route inventories onto owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining large route/name inventory tuples that still live locally in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, so the source-tree anchor-contract suite reads that owner-surface contract from `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of restating it in the consumer test module.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` with plain owner-owned grouped name inventories for the live source-tree support surface that `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` is currently restating locally. Keep this bounded to the existing local tuples in that test module:
  - moved source-tree class/function/constant surface groups
  - routed compiled-pattern contract groups
  - centralized manifest-path and retired-shared-support name groups
  - moved report-contract and routed source-tree-suite assertion helper groups
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to consume those owner-owned groups from `source_tree_benchmark_anchor_support` and delete the local tuple inventories named:
  - `_MOVED_SOURCE_TREE_CLASS_NAMES`
  - `_MOVED_SOURCE_TREE_FUNCTION_NAMES`
  - `_MOVED_SOURCE_TREE_CONSTANT_NAMES`
  - `_ROUTED_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_NAMES`
  - `_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_NAMES`
  - `_ROUTED_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_NAMES`
  - `_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_NAMES`
  - `_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES`
  - `_RETIRED_SHARED_SOURCE_TREE_SUPPORT_NAMES`
  - `_MOVED_REPORT_CONTRACT_HELPER_NAMES`
  - `_ROUTED_REPORT_CONTRACT_HELPER_NAMES`
  - `_ROUTED_SOURCE_TREE_SUITE_ASSERTION_HELPER_NAMES`
- Keep the cleanup structural only:
  - do not move the underlying helper implementations out of `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias shim, or another wrapper layer
  - do not widen into unrelated benchmark-support cleanup outside these duplicated route/name inventories

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_CLASS_NAMES|_MOVED_SOURCE_TREE_FUNCTION_NAMES|_MOVED_SOURCE_TREE_CONSTANT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_NAMES|_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES|_RETIRED_SHARED_SOURCE_TREE_SUPPORT_NAMES|_MOVED_REPORT_CONTRACT_HELPER_NAMES|_ROUTED_REPORT_CONTRACT_HELPER_NAMES|_ROUTED_SOURCE_TREE_SUITE_ASSERTION_HELPER_NAMES) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Constraints
- Keep the task bounded to moving the duplicated source-tree anchor-contract route inventories onto the existing owner module.
- Prefer plain owner-owned tuple constants on `tests/benchmarks/source_tree_benchmark_anchor_support.py` over introducing another abstraction layer.

## Notes
- `RBR-1336` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1336|RBR-1337|RBR-1338|RBR-1339' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still defines eleven top-level local route/name inventory tuples that describe owner-module surface rather than test-local behavior
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns adjacent grouped route inventories for the post-`RBR-1334` collection-replacement surface, so these remaining local tuples are the same kind of contract data still stranded in the consumer test
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `78 passed in 1.05s`
  - `bash -lc "! rg -n '^(_MOVED_SOURCE_TREE_CLASS_NAMES|_MOVED_SOURCE_TREE_FUNCTION_NAMES|_MOVED_SOURCE_TREE_CONSTANT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_NAMES|_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_NAMES|_CENTRALIZED_SOURCE_TREE_MANIFEST_PATH_NAMES|_RETIRED_SHARED_SOURCE_TREE_SUPPORT_NAMES|_MOVED_REPORT_CONTRACT_HELPER_NAMES|_ROUTED_REPORT_CONTRACT_HELPER_NAMES|_ROUTED_SOURCE_TREE_SUITE_ASSERTION_HELPER_NAMES) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because those local route/name inventory tuples still exist, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
