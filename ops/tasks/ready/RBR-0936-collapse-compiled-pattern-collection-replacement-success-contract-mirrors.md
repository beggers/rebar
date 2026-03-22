# RBR-0936: Collapse compiled-pattern collection/replacement success contract mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern collection/replacement success mirror table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the contract section derives its five-row surface directly from the tracked `benchmarks/workloads/collection_replacement_boundary.py` manifest it already validates instead of maintaining a second handwritten `CompiledPatternModuleCollectionReplacementSuccessCase` layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these detached mirror structures:
  - `class CompiledPatternModuleCollectionReplacementSuccessCase`
  - `COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked collection/replacement manifest:
  - use `COLLECTION_REPLACEMENT_MANIFEST_PATH` with `_selected_manifest_workloads(..., include_workload=_is_collection_replacement_compiled_pattern_success_workload)`;
  - reuse existing workload payload helpers such as `workload_to_payload(...)` / `workload_from_payload(...)` when projecting the `-contract` rows; and
  - do not add a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by these five workload ids.
- Preserve the current tracked workload surface exactly while routing it through the manifest:
  - the selected workload ids still resolve, in order, to `module-split-literal-warm-str-compiled-pattern`, `module-findall-literal-purged-bytes-compiled-pattern`, `module-finditer-literal-warm-str-compiled-pattern`, `module-sub-literal-warm-str-compiled-pattern`, then `module-subn-literal-purged-bytes-compiled-pattern`;
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same order;
  - the payload round-trip checks still prove `use_compiled_pattern is True`, the same `count` and `maxsplit` values, no `expected_exception`, no `haystack_text_model`, and the same `str` versus `bytes` payload typing for pattern, haystack, and replacement payloads; and
  - the anchor contract still resolves the same five `-contract` ids to `workflow-module-split-str-compiled-pattern`, `workflow-module-findall-bytes-compiled-pattern`, `workflow-module-finditer-str-compiled-pattern`, `workflow-module-sub-str-compiled-pattern`, and `workflow-module-subn-bytes-compiled-pattern`.
- Keep the callback/probe coverage anchored to the same behavior:
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_workloads(...)` still covers the same five rows;
  - `test_compiled_pattern_module_collection_replacement_success_callbacks_precompile_first_argument_before_timing(...)` still proves the same build-call and callback-call expectations for those five rows, but it must stop depending on tuple positions from the deleted mirror table; and
  - the contract still compares CPython results for the same five rows through `_run_cpython_compiled_pattern_module_collection_replacement_success_workload(...)`.
- Follow the in-file live-selector pattern already used by the compiled-pattern wrong-text-model and compiled-pattern `module.compile` success sections instead of introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleCollectionReplacementSuccessCase|COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    _is_collection_replacement_compiled_pattern_success_workload,
    _selected_manifest_workloads,
)

workloads = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    )
)

assert workloads == (
    "module-split-literal-warm-str-compiled-pattern",
    "module-findall-literal-purged-bytes-compiled-pattern",
    "module-finditer-literal-warm-str-compiled-pattern",
    "module-sub-literal-warm-str-compiled-pattern",
    "module-subn-literal-purged-bytes-compiled-pattern",
)
print("ok", len(workloads))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, fixture changes, or feature work.
- Preserve the current five-row benchmark contract exactly. The point is to delete one benchmark-owner mirror layer, not to reinterpret which compiled-pattern-first-argument collection/replacement success rows stay on the shared benchmark surface.

## Notes
- `RBR-0936` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0936|RBR-0937|RBR-0938|RBR-0939|RBR-0940' ops/state/backlog.md ops/state/current_status.md || true` returned no reserved follow-on ids in this run; and
  - `rg --files ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked | sed 's#.*/##' | sort | tail -n 8` currently ends at `RBR-0935-publish-module-workflow-compiled-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no blocked task file in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured'` currently passes (`18 passed, 565 deselected, 5 subtests passed in 0.28s`);
  - `rg -n '^(class CompiledPatternModuleCollectionReplacementSuccessCase|COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirrors at lines `13823` and `13835`; and
  - the task-local manifest-selector probe in Acceptance currently passes (`ok 5`), proving the five-row surface already exists in the tracked benchmark workload manifest without the extra benchmark-test case table.
