# RBR-0942: Collapse compiled-pattern module-helper keyword carrier mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the detached compiled-pattern collection/replacement keyword carrier case table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so this contract section derives its eleven-row surface directly from the tracked `benchmarks/workloads/collection_replacement_boundary.py` manifest it already validates instead of maintaining a second handwritten `CompiledPatternModuleKeywordCarrierCase` layer.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these detached mirror structures:
  - `class CompiledPatternModuleKeywordCarrierCase`
  - `COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES`
  - `def _compiled_pattern_module_keyword_carrier_case(...)`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked collection/replacement manifest:
  - use `COLLECTION_REPLACEMENT_MANIFEST_PATH` with `_selected_manifest_workloads(...)`;
  - build the source surface from `_is_collection_replacement_keyword_workload(...)` plus a file-local filter that keeps only compiled-pattern-first-argument module helper keyword carriers with:
    - `workload.use_compiled_pattern is True`
    - `workload.operation in {"module.split", "module.sub", "module.subn"}`
    - `workload.expected_exception is None`
    - `getattr(workload, "haystack_text_model", None) is None`
  - reuse existing payload and callback helpers such as `workload_to_payload(...)`, `workload_from_payload(...)`, `run_benchmark_workload_with_cpython(...)`, `_collection_replacement_keyword_parameter_name(...)`, and `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)` where they fit; and
  - do not introduce a new shared helper module, registry table, or another detached tuple/list/dict/dataclass keyed by the same eleven workload ids.
- Preserve the current tracked workload surface exactly while routing it through the manifest:
  - the selected source workload ids still resolve, in order, to:
    - `module-split-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern`
    - `module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern`
    - `module-sub-count-keyword-warm-str-compiled-pattern`
    - `module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern`
    - `module-sub-count-bool-keyword-warm-str-compiled-pattern`
    - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`
    - `module-subn-count-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-indexlike-keyword-purged-str-compiled-pattern`
    - `module-subn-count-bool-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`
  - the generated contract workloads still use those same ids with a `-contract` suffix in the same order;
  - the payload round-trip checks still prove `use_compiled_pattern is True`, `expected_exception is None`, no `haystack_text_model`, the same `count`/`maxsplit` values, the same `kwargs` values and value types, and the same `str` versus `bytes` payload typing for pattern, haystack, and replacement values; and
  - the bool-count complement coverage still proves the same four rows:
    - `module-sub-count-bool-keyword-warm-str-compiled-pattern`
    - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`
    - `module-subn-count-bool-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`
- Keep the callback/probe coverage anchored to the same behavior:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_rows_until_helper_invocation(...)` still validates all eleven rows through manifest-selected source workloads;
  - `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements(...)` still checks the same four bool rows without depending on the deleted case table;
  - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(...)` and `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads(...)` still cover the same eleven rows, but they must stop parameterizing over the deleted mirror constants; and
  - `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(...)` still proves the same precompile-first behavior for the split/sub/subn anchor examples, including the `purged` rows appending `("purge",)`, but it must stop calling the deleted case lookup helper.
- Follow the in-file live-selector pattern already used by the compiled-pattern wrong-text-model, collection/replacement success, module-boundary success, and `module.compile(..., flags=...)` sections instead of introducing another bespoke representation layer.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword and not keyword_error'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleKeywordCarrierCase|COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES|def _compiled_pattern_module_keyword_carrier_case)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    _is_collection_replacement_keyword_workload,
    _selected_manifest_workloads,
)

workloads = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=lambda workload: (
            _is_collection_replacement_keyword_workload(workload)
            and workload.use_compiled_pattern
            and workload.operation in {"module.split", "module.sub", "module.subn"}
            and workload.expected_exception is None
            and getattr(workload, "haystack_text_model", None) is None
        ),
    )
)

assert workloads == (
    "module-split-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
    "module-sub-count-keyword-warm-str-compiled-pattern",
    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
    "module-sub-count-bool-keyword-warm-str-compiled-pattern",
    "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
    "module-subn-count-keyword-purged-bytes-compiled-pattern",
    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
    "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
)

print("ok", len(workloads))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, correctness fixtures, reports, or tracked state files in this run.
- Preserve the current eleven-row benchmark contract exactly. The point is to delete one more benchmark-owner mirror layer, not to reinterpret which compiled-pattern-first-argument module helper keyword-carrier rows stay on the shared benchmark surface.

## Notes
- `RBR-0942` is the next available task id in the current checkout:
  - `rg -n 'RBR-0942|RBR-0943|RBR-0944|RBR-0945|RBR-0946' ops/state/backlog.md ops/state/current_status.md` returned no reserved ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0941-catch-up-raw-module-subn-keyword-error-bytes-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword and not keyword_error'` currently passes (`26 passed, 568 deselected`);
  - `rg -n '^(class CompiledPatternModuleKeywordCarrierCase|COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES|def _compiled_pattern_module_keyword_carrier_case)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirrors at lines `13598`, `13610`, and `13783`; and
  - the task-local manifest-selector probe in Acceptance currently passes (`ok 11`), proving the eleven-row surface already exists in the tracked collection/replacement workload manifest without the extra handwritten case table.

## Completion
- Replaced the detached compiled-pattern module-helper keyword carrier class/table in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with manifest-selected live workloads sourced from `COLLECTION_REPLACEMENT_MANIFEST_PATH` plus an in-file selector that keeps the exact eleven compiled-pattern-first-argument keyword-carrier rows.
- Reworked the contract helpers and tests in that file so the generated `-contract` workloads, payload round-trip checks, bool-count complement coverage, callback-time keyword materialization checks, probe coverage, and precompile-first anchor checks all operate on manifest-selected `Workload` objects instead of a handwritten mirror layer.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword and not keyword_error'`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleKeywordCarrierCase|COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES|def _compiled_pattern_module_keyword_carrier_case)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - the task-local manifest-selector probe from Acceptance, which still resolved the expected eleven workload ids and printed `ok 11`
