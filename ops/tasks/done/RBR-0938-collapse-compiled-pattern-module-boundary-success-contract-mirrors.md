# RBR-0938: Collapse compiled-pattern module-boundary success contract mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern module-boundary success case tables from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the contract section derives its eight-row surface directly from the tracked `benchmarks/workloads/module_boundary.py` manifest it already validates instead of maintaining a second handwritten `CompiledPatternModuleBoundarySuccessCase` layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these detached mirror structures:
  - `class CompiledPatternModuleBoundarySuccessCase`
  - `COMPILED_PATTERN_MODULE_BOUNDARY_LITERAL_SUCCESS_CASES`
  - `COMPILED_PATTERN_MODULE_BOUNDARY_BOUNDED_WILDCARD_SUCCESS_CASES`
  - `COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES`
  - `COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked module-boundary manifest:
  - use `MODULE_BOUNDARY_MANIFEST_PATH` with `_selected_manifest_workloads(...)`;
  - build the success surface from the existing selectors `_is_module_workflow_compiled_pattern_literal_success_workload`, `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload`, and `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload`;
  - reuse existing workload payload helpers such as `workload_to_payload(...)` and `workload_from_payload(...)` when building the `-contract` rows; and
  - do not add a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by these eight workload ids.
- Preserve the current tracked workload surface exactly while routing it through the manifest:
  - the selected source workload ids still resolve, in order, to `module-search-literal-warm-hit-str-compiled-pattern`, `module-match-literal-warm-hit-str-compiled-pattern`, `module-fullmatch-literal-purged-hit-bytes-compiled-pattern`, `module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern`, `module-match-bounded-wildcard-warm-hit-str-compiled-pattern`, `module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern`, `module-search-verbose-regression-warm-hit-bytes-compiled-pattern`, then `module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern`;
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same order;
  - the payload round-trip checks still prove `use_compiled_pattern is True`, the same `flags`, no `expected_exception`, no `haystack_text_model`, and the same `str` versus `bytes` payload typing for pattern and haystack payloads; and
  - the verbose-bytes anchor contract still resolves the same two `-contract` ids to `workflow-module-search-bytes-verbose-regression-compiled-pattern` and `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`.
- Keep the callback/probe coverage anchored to the same behavior:
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_success_workloads(...)` still covers the same eight rows;
  - `test_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(...)` still proves the same compile-call, optional purge-call, and helper-callback expectations for those eight rows, but it must stop depending on tuple positions from the deleted mirror table; and
  - the contract still compares CPython results for the same eight rows through `_run_cpython_compiled_pattern_module_boundary_success_workload(...)`.
- Follow the in-file live-selector pattern already used by the compiled-pattern wrong-text-model and compiled-pattern `module.compile` success sections instead of introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_boundary_success or module_boundary_manifest_keeps_compiled_pattern_module_compile or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleBoundarySuccessCase|COMPILED_PATTERN_MODULE_BOUNDARY_LITERAL_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_BOUNDED_WILDCARD_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _selected_manifest_workloads,
)

selectors = (
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
)
workloads = tuple(
    workload.workload_id
    for selector in selectors
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=selector,
    )
)

assert workloads == (
    "module-search-literal-warm-hit-str-compiled-pattern",
    "module-match-literal-warm-hit-str-compiled-pattern",
    "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
    "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
    "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
    "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
    "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
    "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
)
print("ok", len(workloads))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, fixture changes, or feature work.
- Preserve the current eight-row benchmark contract exactly. The point is to delete one benchmark-owner mirror layer, not to reinterpret which compiled-pattern-first-argument successful module-boundary rows stay on the shared benchmark surface.

## Notes
- `RBR-0938` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0938|RBR-0939|RBR-0940|RBR-0941|RBR-0942' ops/state/backlog.md ops/state/current_status.md || true` returned no reserved follow-on ids in this run; and
  - `rg --files ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked | sed 's#.*/##' | sort | tail -n 8` currently ends at `RBR-0937-catch-up-compiled-pattern-module-helper-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no blocked task file in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_boundary_success or module_boundary_manifest_keeps_compiled_pattern_module_compile or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured'` currently passes (`29 passed, 563 deselected, 25 subtests passed`);
  - `rg -n '^(class CompiledPatternModuleBoundarySuccessCase|COMPILED_PATTERN_MODULE_BOUNDARY_LITERAL_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_BOUNDED_WILDCARD_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_VERBOSE_BYTES_SUCCESS_CASES|COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` now returns no matches; and
  - the task-local selector probe in Acceptance currently passes (`ok 8`), proving the eight-row surface already exists in the tracked module-boundary workload manifest without the extra benchmark-test case tables.

## Completion Note
- 2026-03-22: Replaced the detached compiled-pattern module-boundary success case tables with live source-workload selectors over `benchmarks/workloads/module_boundary.py`, kept the eight workload ids and `-contract` ids in the same order, preserved the payload round-trip and verbose-bytes anchor checks, and reworked the callback expectations to derive from the selected manifest workloads instead of tuple-indexed mirror cases. Verified with the targeted pytest command, the mirror-name grep returning no matches, and the selector probe returning `ok 8`.
