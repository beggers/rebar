## RBR-1409: Move the compiled-pattern module-compile standard definitions onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining source-tree-owned standard-definition export from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns the compiled-pattern module-compile owner specs, but `tests/benchmarks/benchmark_test_support.py` still owns `_build_compiled_pattern_module_compile_standard_benchmark_definitions(...)` and `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`.
- Move that export seam onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only generic helpers and neutral contract primitives instead of another source-tree-specific standard-definition lane.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete this source-tree-owned compiled-pattern module-compile standard-definition surface from `tests/benchmarks/benchmark_test_support.py`:
  - `_build_compiled_pattern_module_compile_standard_benchmark_definitions(...)`
  - `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
- Recreate that moved surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wired to the existing owner-spec tuples already defined there:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
- Preserve the existing standard-definition names, ordering, and anchor-definition behavior for the eight compiled-pattern module-compile entries.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so ownership assertions and the combined standard-definition inventory treat the compiled-pattern module-compile standard-definition tuple as source-tree-owned instead of shared-support-owned.
- Update `tests/benchmarks/test_benchmark_test_support.py` so shared-support ownership assertions stop expecting the moved builder/export on `benchmark_test_support.py` and instead verify they now live on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` only as needed so their explicit standard-definition inventories import the moved compiled-pattern module-compile tuple from source-tree owner support instead of shared support.
- Keep genuinely shared compiled-pattern module-contract helpers in `tests/benchmarks/benchmark_test_support.py`, including the workload selectors, shared contract dataclasses, and generic signature/build-call helpers this task does not move.
- Do not widen into the compiled-pattern module-helper lane, collection/replacement keyword-contract surfaces, pattern-boundary owner support, workload manifests, reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k compiled_pattern_module_compile_standard`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k owns_compiled_pattern_module_compile_standard_definitions`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(def _build_compiled_pattern_module_compile_standard_benchmark_definitions|COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS =)' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1409\\b" ops/state/backlog.md ops/state/current_status.md ops/tasks ops/state/decision_log.md` hit only historical note text inside completed `RBR-1407` and `RBR-1408` task files; there was no reserved future-id use or live duplicate for `RBR-1409`.
- Candidate selection in this run:
  - The first viable post-JSON simplification was the compiled-pattern module-compile standard-definition seam because the owner specs already live in `tests/benchmarks/source_tree_benchmark_anchor_support.py` while the shared support file still exports the builder/tuple.
  - `rg -n "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS|_build_compiled_pattern_module_compile_standard_benchmark_definitions" tests/benchmarks/benchmark_test_support.py tests/benchmarks/*.py` shows the builder/export still originate in `tests/benchmarks/benchmark_test_support.py`, while the owner-facing inventory tests in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and adjacent benchmark-owner tests consume that shared export.
  - I stopped after this first viable candidate because it removes one complete owner-boundary export layer from the shared benchmark-support module without depending on unrelated feature work.
- Verification in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k compiled_pattern_module_compile_standard` -> `3 passed, 120 deselected`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k owns_compiled_pattern_module_compile_standard_definitions` -> `1 passed, 179 deselected`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> passed
  - `bash -lc "! rg -n '^(def _build_compiled_pattern_module_compile_standard_benchmark_definitions|COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS =)' tests/benchmarks/benchmark_test_support.py"` currently fails only because this exact shared-support export is still present, which is the cleanup this task queues.
- Completion:
  - Moved `_build_compiled_pattern_module_compile_standard_benchmark_definitions(...)` and `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS` from `tests/benchmarks/benchmark_test_support.py` to `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wiring the builder to the existing `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`.
  - Updated the source-tree, shared-support, pattern-boundary, and collection-replacement tests so their ownership assertions and explicit standard-definition inventories now import the compiled-pattern module-compile tuple from source-tree owner support.
  - Verification in this implementation run:
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k compiled_pattern_module_compile_standard` -> `3 passed, 120 deselected`
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k owns_compiled_pattern_module_compile_standard_definitions` -> `1 passed, 179 deselected`
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k standard_definitions_are_reused_by_standard_inventory` -> `1 passed, 26 deselected`
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k standard_definitions_are_reused_by_standard_inventory` -> `1 passed, 154 deselected`
    - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k "source_tree_compiled_pattern_module_compile_standard_definition_helpers or compiled_pattern_module_compile_standard_benchmark_definitions_are_source_tree_owned"` -> `2 passed, 121 deselected`
    - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> passed
    - `bash -lc "! rg -n '^(def _build_compiled_pattern_module_compile_standard_benchmark_definitions|COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS =)' tests/benchmarks/benchmark_test_support.py"` -> passed
