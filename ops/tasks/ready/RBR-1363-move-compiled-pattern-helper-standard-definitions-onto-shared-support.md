# RBR-1363: Move compiled-pattern helper standard definitions onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for compiled-pattern helper standard benchmark definitions so that `tests/benchmarks/benchmark_test_support.py` owns that shared definition block directly instead of routing it through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Define `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` in `tests/benchmarks/benchmark_test_support.py` and include it in `STANDARD_BENCHMARK_DEFINITIONS` there without routing through `source_tree_support`.
- Delete the local `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` assignment from `tests/benchmarks/source_tree_benchmark_anchor_support.py` and remove it from `SOURCE_TREE_LOCAL_COMPILED_PATTERN_WRONG_TEXT_MODEL_ASSIGNMENT_NAMES` instead of leaving an alias shim or routed-owner placeholder behind.
- Update the touched tests so the helper standard-definition block is treated as shared-support-owned rather than source-tree-owned, while preserving the existing owner-block ordering between compiled-pattern module-compile definitions and pattern-boundary definitions.
- Keep the cleanup bounded to the helper standard-definition block:
  - do not move `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
  - do not rewrite the broader source-tree combined-slice expectation machinery
  - do not change benchmark selection semantics, anchored workload IDs, or runtime behavior

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'test_standard_benchmark_definitions_keep_owner_blocks_in_order'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally or test_source_tree_standard_definitions_export_stays_owned_by_source_tree'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `rg -n '^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS|anchor_support\\.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the owner transit layer over moving it sideways; the helper definition block already depends only on shared manifest paths, shared selector helpers, and shared correctness/workload signatures from `tests/benchmarks/benchmark_test_support.py`.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-specific combined-slice expectations and the owner surfaces that still genuinely belong there after this cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1363|RBR-1364|RBR-1365' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` locally even though each definition is built entirely from shared support helpers on `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/benchmark_test_support.py` still pulls that owner block into `STANDARD_BENCHMARK_DEFINITIONS` through `source_tree_support`
  - `tests/benchmarks/test_benchmark_test_support.py` still references `anchor_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still counts that name as source-tree-local inventory
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'test_standard_benchmark_definitions_keep_owner_blocks_in_order'` passed with `7 passed, 163 deselected in 0.15s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally or test_source_tree_standard_definitions_export_stays_owned_by_source_tree'` passed with `2 passed, 102 deselected in 0.16s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `rg -n '^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared support module does not yet define that owner block, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because the helper definition block still lives on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS|anchor_support\\.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because the shared benchmark support and benchmark-support tests still route that owner block through the source-tree module, and that failure belongs exactly to this cleanup
