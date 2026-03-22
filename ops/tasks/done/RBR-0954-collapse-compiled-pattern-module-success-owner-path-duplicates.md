# RBR-0954: Collapse compiled-pattern module success owner-path duplicates

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining collection-replacement versus module-boundary success helper/test copies from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern success benchmark contract runs through one file-local owner-spec path instead of maintaining paired payload round-trip helpers, paired callback/precompile expectation helpers, paired CPython runner helpers, and paired manifest/probe/precompile test bodies that only differ by owner-specific metadata.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on these duplicated collection-replacement versus module-boundary success helpers:
  - `def _assert_compiled_pattern_module_collection_replacement_success_payload_round_trip(...)`
  - `def _compiled_pattern_module_collection_replacement_success_expected_callback_result(...)`
  - `def _compiled_pattern_module_collection_replacement_success_expected_build_calls(...)`
  - `def _compiled_pattern_module_collection_replacement_success_expected_callback_call(...)`
  - `def _run_cpython_compiled_pattern_module_collection_replacement_success_workload(...)`
  - `def _assert_compiled_pattern_module_boundary_success_payload_round_trip(...)`
  - `def _compiled_pattern_module_boundary_success_expected_build_calls(...)`
  - `def _compiled_pattern_module_boundary_success_expected_callback_call(...)`
  - `def _run_cpython_compiled_pattern_module_boundary_success_workload(...)`
- Replace those paired helpers with one file-local owner-spec-driven success contract surface that stays explicit but smaller than the current duplicated structure:
  - keep it local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - it may extend `CompiledPatternModuleSuccessOwnerSpec` or introduce a tiny adjacent frozen spec/helper surface;
  - each owner path should carry only the metadata that actually differs between collection/replacement and module-boundary success coverage, such as the source selector bundle, contract filename, note surface, expected source workload ids, CPython execution shape, and callback expectation shape;
  - do not add a shared helper module, registry, or checked-in data layer.
- Preserve the current live source-workload surfaces exactly:
  - the collection/replacement owner path still resolves, in order, to:
    - `module-split-literal-warm-str-compiled-pattern`
    - `module-findall-literal-purged-bytes-compiled-pattern`
    - `module-finditer-literal-warm-str-compiled-pattern`
    - `module-sub-literal-warm-str-compiled-pattern`
    - `module-subn-literal-purged-bytes-compiled-pattern`
  - the module-boundary owner path still resolves, in order, to:
    - `module-search-literal-warm-hit-str-compiled-pattern`
    - `module-match-literal-warm-hit-str-compiled-pattern`
    - `module-fullmatch-literal-purged-hit-bytes-compiled-pattern`
    - `module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern`
    - `module-match-bounded-wildcard-warm-hit-str-compiled-pattern`
    - `module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern`
    - `module-search-verbose-regression-warm-hit-bytes-compiled-pattern`
    - `module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern`
  - both owner paths still generate `-contract` workload ids in the same order and still keep `use_compiled_pattern is True`.
- Collapse the duplicated success test bodies onto one owner-spec-driven structure while preserving behavior:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_rows_until_helper_invocation(...)` and `test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_success_rows_until_helper_invocation(...)` become one parametrized or equivalently shared owner-spec test body;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_workloads(...)` and `test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_success_workloads(...)` become one parametrized or equivalently shared owner-spec test body; and
  - `test_compiled_pattern_module_collection_replacement_success_callbacks_precompile_first_argument_before_timing(...)` and `test_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(...)` become one parametrized or equivalently shared owner-spec test body.
- The shared owner-spec-driven success contract must preserve the current owner-specific semantics instead of flattening them:
  - both owner paths still build contract workloads through `_compiled_pattern_module_success_manifest_payload(...)`, `_compiled_pattern_module_success_workload(...)`, `_compiled_pattern_module_success_source_workloads(...)`, and `_compiled_pattern_module_success_manifest(...)` or equivalent file-local successors rather than a detached handwritten workload layer;
  - both owner paths still keep `haystack_text_model is None` on the generated contract workloads and still preserve the same `str` versus `bytes` payload typing for pattern and haystack values;
  - the collection/replacement owner path still preserves replacement payload typing when present, still compares its manifest-preservation path against the same CPython split/findall/finditer/sub/subn behavior, and still returns:
    - `"module-result"` for `module.split` and `module.sub`
    - `["module-finditer-result"]` for `module.finditer`
    - `("module-result", 0)` for `module.subn`
  - the module-boundary owner path still compares its manifest-preservation path against the same CPython search/match/fullmatch behavior and still returns `"module-result"` from the precompile-first callback path;
  - purged success rows for both owner paths still append `("purge",)` after the initial `("compile", pattern, flags)` build call, while warm rows still keep only the compile call;
  - the collection/replacement callback-call expectations still preserve the same positional argument order for split/findall/finditer/sub/subn; and
  - the module-boundary callback-call expectations still preserve the same `(operation, haystack_payload, 0, {})` shape for search/match/fullmatch after the precompiled pattern is substituted into the first callback slot.
- Keep the success-anchor coverage unchanged:
  - do not broaden into the compile-success or compile-keyword sections;
  - do not alter the dedicated verbose-bytes anchor test unless the shared owner-spec cleanup requires only a minimal mechanical rename or parameterization while preserving its current anchored workload ids and case ids exactly.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success'`
- `bash -lc "! rg -n 'def _assert_compiled_pattern_module_collection_replacement_success_payload_round_trip\\(|def _compiled_pattern_module_collection_replacement_success_expected_callback_result\\(|def _compiled_pattern_module_collection_replacement_success_expected_build_calls\\(|def _compiled_pattern_module_collection_replacement_success_expected_callback_call\\(|def _run_cpython_compiled_pattern_module_collection_replacement_success_workload\\(|def _assert_compiled_pattern_module_boundary_success_payload_round_trip\\(|def _compiled_pattern_module_boundary_success_expected_build_calls\\(|def _compiled_pattern_module_boundary_success_expected_callback_call\\(|def _run_cpython_compiled_pattern_module_boundary_success_workload\\(|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_workloads|test_compiled_pattern_module_collection_replacement_success_callbacks_precompile_first_argument_before_timing|test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_success_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_success_workloads|test_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _compiled_pattern_module_success_source_workloads,
)

collection_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_success_source_workloads(
        _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC
    )
)
boundary_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_success_source_workloads(
        _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC
    )
)

assert collection_ids == (
    "module-split-literal-warm-str-compiled-pattern",
    "module-findall-literal-purged-bytes-compiled-pattern",
    "module-finditer-literal-warm-str-compiled-pattern",
    "module-sub-literal-warm-str-compiled-pattern",
    "module-subn-literal-purged-bytes-compiled-pattern",
)
assert boundary_ids == (
    "module-search-literal-warm-hit-str-compiled-pattern",
    "module-match-literal-warm-hit-str-compiled-pattern",
    "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
    "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
    "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
    "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
    "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
    "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
)

print("ok", len(collection_ids), len(boundary_ids))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/module_boundary.py`, `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.
- Prefer deleting duplicate owner-path helpers and test bodies over introducing another detached id-keyed helper layer.

## Notes
- `RBR-0954` is the next available task id in the current checkout:
  - `rg -n 'RBR-0954|RBR-0955|RBR-0956|RBR-0957|RBR-0958' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0953-catch-up-module-replacement-count-alias-keyword-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success'` currently passes (`42 passed, 582 deselected`);
  - the owner-surface probe in Verification currently passes (`ok 5 8`), proving both success surfaces already exist directly on the live manifest-selected workload path; and
  - the negative `rg` check in Verification currently fails only because the duplicate success helper/test layer named in this task is still present in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Completion Note
- Landed a file-local owner-spec cleanup in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: the collection/replacement and module-boundary compiled-pattern success paths now share one owner-spec-driven payload/build/probe/callback test surface, the duplicate helper/test names called out in this task are gone, the source workload ids still resolve to the same 5-row and 8-row owner surfaces in the same order, and the targeted pytest/rg/owner-surface checks all pass in this checkout.
