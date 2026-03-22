# RBR-0932: Collapse compiled-pattern wrong-text-model contract mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern wrong-text-model contract mirrors from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the collection/replacement and module-boundary sections derive their bounded rows directly from the tracked benchmark manifests they already validate instead of maintaining a second handwritten `CompiledPatternModuleWrongTextModelCase` layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached mirror structures:
  - `class CompiledPatternModuleWrongTextModelCase`
  - `COMPILED_PATTERN_MODULE_WRONG_TEXT_MODEL_CASES`
  - `COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_CASES`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked manifests already loaded in this file:
  - use `COLLECTION_REPLACEMENT_MANIFEST_PATH` with `_selected_manifest_workloads(..., include_workload=_is_collection_replacement_wrong_text_model_workload)` for the collection/replacement slice;
  - use `MODULE_BOUNDARY_MANIFEST_PATH` with `_selected_manifest_workloads(..., include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload)` for the module-boundary slice;
  - reuse existing workload payload helpers such as `workload_to_payload(...)` / `workload_from_payload(...)` when projecting contract rows;
  - do not add a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by these workload ids; and
  - keep any replacement helpers local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Preserve the live tracked wrong-text-model surfaces exactly while routing them through those selectors:
  - the collection/replacement source workload ids still resolve, in order, to `module-split-on-bytes-string-purged-str-compiled-pattern`, `module-findall-on-str-string-purged-bytes-compiled-pattern`, `module-finditer-on-bytes-string-warm-str-compiled-pattern`, `module-sub-on-bytes-string-warm-str-compiled-pattern`, then `module-subn-on-str-string-purged-bytes-compiled-pattern`;
  - the module-boundary source workload ids still resolve, in order, to `module-search-on-bytes-string-warm-str-compiled-pattern`, `module-match-on-str-string-purged-bytes-compiled-pattern`, then `module-fullmatch-on-bytes-string-warm-str-compiled-pattern`;
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same order for each surface;
  - the contract projections still preserve `use_compiled_pattern is True`, the same `haystack_text_model` values, the same `expected_exception` payloads, and the same text-vs-bytes payload typing for pattern, haystack, and replacement payloads; and
  - the two contract tests still compare CPython exceptions against `run_benchmark_workload_with_cpython(...)` for the same eight rows.
- Keep the callback/probe coverage anchored to the same bounded behavior:
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_wrong_text_model_workloads(...)` still covers the same five collection/replacement rows;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_wrong_text_model_workloads(...)` still covers the same three module-boundary rows;
  - `test_compiled_pattern_module_helper_wrong_text_model_callbacks_precompile_first_argument_before_timing(...)` still proves the same five collection/replacement rows with the same build-call and callback-call expectations, but it must stop depending on tuple positions from the deleted mirror table; and
  - `test_compiled_pattern_module_boundary_wrong_text_model_callbacks_precompile_first_argument_before_timing(...)` still proves the same three module-boundary rows with the same build-call and callback-call expectations, likewise without depending on tuple positions from the deleted mirror table.
- Follow the in-file live-selector pattern already used by the direct Pattern wrong-text-model section around `_pattern_helper_collection_replacement_wrong_text_model_workloads()` rather than introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleWrongTextModelCase|COMPILED_PATTERN_MODULE_WRONG_TEXT_MODEL_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_collection_replacement_wrong_text_model_workload,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _selected_manifest_workloads,
)

collection = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_wrong_text_model_workload,
    )
)
module = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
    )
)

assert collection == (
    "module-split-on-bytes-string-purged-str-compiled-pattern",
    "module-findall-on-str-string-purged-bytes-compiled-pattern",
    "module-finditer-on-bytes-string-warm-str-compiled-pattern",
    "module-sub-on-bytes-string-warm-str-compiled-pattern",
    "module-subn-on-str-string-purged-bytes-compiled-pattern",
)
assert module == (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)
print("ok", len(collection), len(module))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, correctness fixtures, reports, or tracked project-state files in this run.
- Preserve the current compiled-pattern wrong-text-model contract coverage exactly. The point is to delete one more benchmark-owner mirror layer, not to reinterpret which tracked rows stay on the shared benchmark surface.

## Notes
- `RBR-0932` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0932|RBR-0933|RBR-0934|RBR-0935|RBR-0936' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run; and
  - the highest tracked task file currently present is `RBR-0931-publish-module-workflow-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured'` currently passes (`27 passed, 554 deselected, 8 subtests passed in 0.43s`);
  - `rg -n '^(class CompiledPatternModuleWrongTextModelCase|COMPILED_PATTERN_MODULE_WRONG_TEXT_MODEL_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirrors at lines `15479`, `15493`, and `15577`; and
  - the task-local live-selector probe in Acceptance currently passes (`ok 5 3`), proving the tracked benchmark manifests already expose the same bounded collection/replacement and module-boundary wrong-text-model rows without the detached handwritten case table.

## Completion
- Completed on 2026-03-22.
- Removed the detached compiled-pattern wrong-text-model case tables from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and replaced them with file-local selectors over `collection_replacement_boundary.py` and `module_boundary.py`.
- Kept the same five collection/replacement rows and three module-boundary rows, projecting `-contract` workloads directly from manifest-backed `Workload` payloads while preserving `use_compiled_pattern`, haystack text-model fields, expected exceptions, and text-vs-bytes payload typing.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleWrongTextModelCase|COMPILED_PATTERN_MODULE_WRONG_TEXT_MODEL_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - the acceptance selector probe (`ok 5 3`)
