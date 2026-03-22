# RBR-0934: Collapse compiled-pattern module.compile success contract mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern `module.compile` success mirror table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the contract section derives its four-row surface directly from the tracked `benchmarks/workloads/module_boundary.py` manifest it already validates instead of maintaining a second handwritten `CompiledPatternModuleCompileSuccessCase` layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these detached mirror structures:
  - `class CompiledPatternModuleCompileSuccessCase`
  - `COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CASES`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked module-boundary manifest:
  - use `MODULE_BOUNDARY_MANIFEST_PATH` with `_selected_manifest_workloads(...)`;
  - reuse the existing selectors `_is_module_workflow_compiled_pattern_compile_literal_success_workload` and `_is_module_workflow_compiled_pattern_compile_named_group_success_workload`;
  - reuse existing workload payload helpers such as `workload_to_payload(...)` / `workload_from_payload(...)` when projecting the `-contract` rows; and
  - do not add a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by these four workload ids.
- Preserve the current tracked workload surface exactly while routing it through the manifest:
  - the selected literal success workload ids still resolve, in order, to `module-compile-literal-warm-str-compiled-pattern` then `module-compile-literal-purged-bytes-compiled-pattern`;
  - the selected named-group success workload ids still resolve, in order, to `module-compile-named-group-warm-str-compiled-pattern` then `module-compile-named-group-purged-bytes-compiled-pattern`;
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same combined order;
  - the payload round-trip checks still prove `use_compiled_pattern is True`, the same `flags`, no `expected_exception`, no `haystack_text_model`, and the same `str` vs `bytes` pattern payload typing; and
  - the anchor contract still resolves the same four `-contract` ids to `workflow-module-compile-str-compiled-pattern`, `workflow-module-compile-bytes-compiled-pattern`, `workflow-module-compile-str-compiled-pattern-named-group`, and `workflow-module-compile-bytes-compiled-pattern-named-group`.
- Keep the callback/probe coverage anchored to the same behavior:
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_workloads(...)` still covers the same four rows;
  - `test_compiled_pattern_module_compile_success_callbacks_precompile_first_argument_before_timing(...)` still proves the same build-call expectations for the four rows:
    - `module-compile-literal-warm-str-compiled-pattern`: `[("compile", "abc", 0)]`
    - `module-compile-literal-purged-bytes-compiled-pattern`: `[("compile", b"abc", 0), ("purge",)]`
    - `module-compile-named-group-warm-str-compiled-pattern`: `[("compile", "(?P<word>abc)", 0)]`
    - `module-compile-named-group-purged-bytes-compiled-pattern`: `[("compile", b"(?P<word>abc)", 0), ("purge",)]`
  - that callback test still proves the callback returns the precompiled pattern object and that the last recorded call is `("compile", compiled_pattern, 0)`.
- Follow the in-file live-selector pattern already used by the compiled-pattern wrong-text-model contract section rather than introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success or module_boundary_manifest_keeps_compiled_pattern_compile_literal_success_rows_measured or module_boundary_manifest_keeps_compiled_pattern_compile_named_group_success_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleCompileSuccessCase|COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_module_workflow_compiled_pattern_compile_literal_success_workload,
    _is_module_workflow_compiled_pattern_compile_named_group_success_workload,
    _selected_manifest_workloads,
)

literal = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_compile_literal_success_workload,
    )
)
named = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_compile_named_group_success_workload,
    )
)

assert literal == (
    "module-compile-literal-warm-str-compiled-pattern",
    "module-compile-literal-purged-bytes-compiled-pattern",
)
assert named == (
    "module-compile-named-group-warm-str-compiled-pattern",
    "module-compile-named-group-purged-bytes-compiled-pattern",
)
print("ok", len(literal), len(named))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, fixture changes, or feature work.
- Preserve the current four-row benchmark contract exactly. The point is to delete one benchmark-owner mirror layer, not to reinterpret which compiled-pattern `module.compile` success rows stay on the shared benchmark surface.

## Notes
- `RBR-0934` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0934|RBR-0935|RBR-0936|RBR-0937|RBR-0938' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run; and
  - `rg --files ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked | sed 's#.*/##' | sort | tail -n 8` currently ends at `RBR-0933-catch-up-pattern-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success or module_boundary_manifest_keeps_compiled_pattern_compile_literal_success_rows_measured or module_boundary_manifest_keeps_compiled_pattern_compile_named_group_success_rows_measured'` currently passes (`14 passed, 569 deselected in 0.15s`);
  - `rg -n '^(class CompiledPatternModuleCompileSuccessCase|COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirrors at lines `14242` and `14250`; and
  - the task-local manifest-selector probe in Acceptance currently passes (`ok 2 2`), proving the four-row surface already exists in the tracked benchmark workload manifest without the extra benchmark-test case table.

## Completion
- 2026-03-22: Replaced the detached compiled-pattern `module.compile` success case dataclass/table in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with live source-workload selection from `MODULE_BOUNDARY_MANIFEST_PATH`, reusing the existing literal/named-group selectors plus `workload_to_payload(...)` / `workload_from_payload(...)` to project the four `-contract` rows directly from the tracked manifest.
- Preserved the four-row order, the `-contract` ids, the anchor mappings, the round-trip payload expectations, and the callback/probe behavior while following the same in-file source-workload pattern already used by the compiled-pattern wrong-text-model contract section.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success or module_boundary_manifest_keeps_compiled_pattern_compile_literal_success_rows_measured or module_boundary_manifest_keeps_compiled_pattern_compile_named_group_success_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleCompileSuccessCase|COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... PY` selector probe asserting the literal and named-group workload ids still resolve to the same two-row sequences (`ok 2 2`)
