# RBR-0940: Collapse compiled-pattern module.compile keyword case mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached compiled-pattern `module.compile(..., flags=...)` keyword case tables from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the contract section derives its twelve-row surface directly from the tracked `benchmarks/workloads/module_boundary.py` manifest it already validates instead of maintaining a second handwritten keyword-case layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these detached mirror structures:
  - `class CompiledPatternModuleCompileKeywordCase`
  - `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES`
  - `COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES`
- Replace that mirror layer with file-local live selectors or projections over the tracked module-boundary manifest:
  - use `MODULE_BOUNDARY_MANIFEST_PATH` with `_selected_manifest_workloads(...)`;
  - reuse the existing selector functions `_is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload`, `_is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload`, `_is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload`, `_is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload`, `_is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload`, and `_is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload`;
  - keep per-group anchor/signature metadata file-local, but do not introduce a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by the same twelve workload ids.
- Preserve the current tracked workload surface exactly while routing it through the manifest:
  - the selector groups still resolve, in order, to:
    - `int-zero`: `module-compile-flags-int-zero-warm-str-compiled-pattern`, `module-compile-flags-int-zero-purged-bytes-compiled-pattern`
    - `int-zero-named-group`: `module-compile-flags-int-zero-warm-str-compiled-pattern-named-group`, `module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group`
    - `bool-false`: `module-compile-flags-bool-false-warm-str-compiled-pattern`, `module-compile-flags-bool-false-purged-bytes-compiled-pattern`
    - `bool-false-named-group`: `module-compile-flags-bool-false-warm-str-compiled-pattern-named-group`, `module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group`
    - `ignorecase`: `module-compile-flags-ignorecase-warm-str-compiled-pattern`, `module-compile-flags-ignorecase-purged-bytes-compiled-pattern`
    - `ignorecase-named-group`: `module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group`, `module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group`
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same per-group order;
  - the payload round-trip checks still prove `use_compiled_pattern is True`, the same `flags`, the same `kwargs["flags"]` value and type, no `haystack_text_model`, and the same `str` versus `bytes` pattern payload typing;
  - the `ignorecase` and `ignorecase-named-group` rows still carry `_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION`, while the other four groups remain success rows; and
  - the existing per-group contract and anchor filenames plus expected anchor-pair mappings remain unchanged.
- Keep the callback/probe coverage anchored to the same behavior:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_keyword_rows_until_helper_invocation(...)` still validates all six groups through manifest-selected source workloads;
  - `test_compiled_pattern_module_compile_keyword_rows_stay_anchored_to_published_correctness_cases(...)` still checks the same per-group expected anchor pairs without depending on deleted case tuples;
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(...)`, `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_keyword_workloads(...)`, and `test_compiled_pattern_module_compile_keyword_callbacks_precompile_first_argument_before_timing(...)` still cover the same twelve rows, but they must stop parameterizing over the deleted mirror constants; and
  - the callback test still proves the same precompile-first behavior, including the `purged` rows appending `("purge",)` and the `ignorecase` rows raising the same rejection substring.
- Follow the in-file live-selector pattern already used by the compiled-pattern wrong-text-model, collection/replacement success, `module.compile` success, and module-boundary success sections instead of introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_keyword or module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleCompileKeywordCase|COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload,
    _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload,
    _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload,
    _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload,
    _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload,
    _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload,
    _selected_manifest_workloads,
)

selectors = (
    ("int-zero", _is_module_workflow_compiled_pattern_compile_int_zero_keyword_workload),
    (
        "int-zero-named-group",
        _is_module_workflow_compiled_pattern_compile_int_zero_named_group_keyword_workload,
    ),
    ("bool-false", _is_module_workflow_compiled_pattern_compile_bool_false_keyword_workload),
    (
        "bool-false-named-group",
        _is_module_workflow_compiled_pattern_compile_bool_false_named_group_keyword_workload,
    ),
    ("ignorecase", _is_module_workflow_compiled_pattern_compile_ignorecase_keyword_workload),
    (
        "ignorecase-named-group",
        _is_module_workflow_compiled_pattern_compile_ignorecase_named_group_keyword_workload,
    ),
)
expected = {
    "int-zero": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
    ),
    "int-zero-named-group": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
    ),
    "bool-false": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
    ),
    "bool-false-named-group": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
    ),
    "ignorecase": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
    ),
    "ignorecase-named-group": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
    ),
}

for name, selector in selectors:
    observed = tuple(
        workload.workload_id
        for workload in _selected_manifest_workloads(
            MODULE_BOUNDARY_MANIFEST_PATH,
            include_workload=selector,
        )
    )
    assert observed == expected[name], (name, observed)

print("ok", len(selectors))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, fixture changes, or feature work.
- Preserve the current twelve-row benchmark contract exactly. The point is to delete one benchmark-owner mirror layer, not to reinterpret which compiled-pattern-first-argument `module.compile(..., flags=...)` rows stay on the shared benchmark surface.

## Notes
- `RBR-0940` is the next available task id in the current checkout:
  - `rg -n 'RBR-0940|RBR-0941|RBR-0942|RBR-0943|RBR-0944' ops/state/backlog.md ops/state/current_status.md` returned no reserved ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 8` currently ends at `RBR-0939-publish-module-workflow-module-subn-keyword-error-bytes-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_keyword or module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured'` currently passes (`52 passed, 540 deselected, 26 subtests passed`);
  - `rg -n '^(class CompiledPatternModuleCompileKeywordCase|COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_NAMED_GROUP_KEYWORD_CASES|COMPILED_PATTERN_MODULE_COMPILE_ALL_KEYWORD_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirrors; and
  - the selector probe in Acceptance currently passes (`ok 6`), proving the twelve-row surface already exists in `benchmarks/workloads/module_boundary.py` without the extra keyword-case tables.
