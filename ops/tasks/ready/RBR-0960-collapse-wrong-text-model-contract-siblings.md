# RBR-0960: Collapse wrong-text-model contract siblings

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining direct-`Pattern` versus compiled-pattern-module wrong-text-model contract helper/test stacks from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the bounded wrong-text-model benchmark coverage runs through one shared file-local contract surface instead of maintaining two near-identical manifest, payload-round-trip, CPython-expectation, probe, and precompile-first callback layers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on these dedicated wrong-text-model helper stacks:
  - direct-`Pattern` stack:
    - `def _pattern_helper_collection_replacement_wrong_text_model_manifest_payload(...)`
    - `def _pattern_helper_collection_replacement_wrong_text_model_workloads(...)`
    - `def _pattern_helper_collection_replacement_wrong_text_model_manifest(...)`
    - `def _assert_pattern_helper_collection_replacement_wrong_text_model_payload_round_trip(...)`
    - `def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_result(...)`
    - `def _pattern_helper_collection_replacement_wrong_text_model_expected_build_calls(...)`
    - `def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_call(...)`
    - `def _run_cpython_pattern_helper_collection_replacement_wrong_text_model_workload(...)`
  - compiled-pattern-module stack:
    - `def _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip(...)`
    - `def _compiled_pattern_module_helper_wrong_text_model_expected_callback_result(...)`
    - `def _compiled_pattern_module_helper_wrong_text_model_expected_callback_call(...)`
    - `def _run_cpython_compiled_pattern_module_helper_wrong_text_model_workload(...)`
- Replace those siblings with one shared file-local wrong-text-model contract surface that stays explicit but smaller than the current duplicated structure:
  - it may extend `CompiledPatternModuleWrongTextModelOwnerSpec` or add a tiny adjacent frozen spec/helper surface that also covers the direct-`Pattern` owner path;
  - keep the cleanup local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - do not add a shared helper module, registry, or checked-in data layer; and
  - keep the live source workloads anchored to `_selected_manifest_workloads(...)` against the tracked manifests instead of introducing handwritten workload rows.
- Preserve the current bounded source-workload surfaces exactly:
  - the compiled-pattern collection/replacement owner path still resolves, in order, to:
    - `module-split-on-bytes-string-purged-str-compiled-pattern`
    - `module-findall-on-str-string-purged-bytes-compiled-pattern`
    - `module-finditer-on-bytes-string-warm-str-compiled-pattern`
    - `module-sub-on-bytes-string-warm-str-compiled-pattern`
    - `module-subn-on-str-string-purged-bytes-compiled-pattern`
  - the compiled-pattern module-boundary owner path still resolves, in order, to:
    - `module-search-on-bytes-string-warm-str-compiled-pattern`
    - `module-match-on-str-string-purged-bytes-compiled-pattern`
    - `module-fullmatch-on-bytes-string-warm-str-compiled-pattern`
  - the direct-`Pattern` collection/replacement owner path still resolves, in order, to:
    - `pattern-split-on-bytes-string-warm-str`
    - `pattern-sub-on-bytes-string-warm-str`
    - `pattern-subn-on-str-string-purged-bytes`
  - the generated contract rows still append `-contract` to those same source workload ids in the same per-surface order;
  - the compiled-pattern contract rows still keep `use_compiled_pattern is True`;
  - the direct-`Pattern` contract rows still keep `use_compiled_pattern is False`;
  - the compiled-pattern collection/replacement and direct-`Pattern` collection/replacement paths still use manifest id `collection-replacement-boundary`; and
  - the compiled-pattern module-boundary path still uses manifest id `module-boundary`.
- Collapse the duplicate test bodies onto one shared wrong-text-model contract structure while preserving behavior:
  - `test_standard_benchmark_manifest_preserves_pattern_collection_replacement_wrong_text_model_rows_until_helper_invocation(...)` and `test_standard_benchmark_manifest_preserves_compiled_pattern_module_wrong_text_model_rows_until_helper_invocation(...)` become one parametrized or equivalently shared contract test body;
  - `test_run_internal_workload_probe_measures_pattern_helper_collection_replacement_wrong_text_model_workloads(...)` and `test_run_internal_workload_probe_measures_compiled_pattern_module_wrong_text_model_workloads(...)` become one parametrized or equivalently shared contract test body; and
  - `test_pattern_helper_collection_replacement_wrong_text_model_callbacks_precompile_before_timing(...)` and `test_compiled_pattern_module_wrong_text_model_callbacks_precompile_first_argument_before_timing(...)` become one parametrized or equivalently shared contract test body.
- The shared wrong-text-model contract surface must preserve the current direct-`Pattern` versus compiled-pattern-module semantic split instead of flattening behavior:
  - the manifest-preservation path still compares exact CPython `TypeError` text against `run_benchmark_workload_with_cpython(...)` for all three surfaces;
  - the direct-`Pattern` path still preserves the same `pattern.split` / `pattern.sub` / `pattern.subn` callback-call shapes, return values, and cache-mode-dependent build calls;
  - the compiled-pattern-module paths still preserve the same `module.search` / `module.match` / `module.fullmatch` / `module.split` / `module.findall` / `module.finditer` / `module.sub` / `module.subn` callback-call shapes, return values, and compiled-pattern-first-argument behavior;
  - the direct-`Pattern` path still preserves `timing_scope == "pattern-helper-call"`;
  - the compiled-pattern-module paths still preserve `timing_scope == "module-helper-call"`;
  - payload round-trip checks still preserve the same `haystack_text_model`, `expected_exception`, and `str` versus `bytes` payload typing for every surface; and
  - the internal-probe path still measures both adapters on every contract row and still requires `probe["status"] == "measured"` plus `probe["median_ns"] > 0`.
- Keep the targeted direct-`Pattern` coverage explicit:
  - `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases(...)` stays present or is replaced by an equivalent focused assertion that still proves the same three anchored case-id pairs; and
  - `test_pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time(...)` stays present or is replaced by an equivalent focused assertion that still proves haystack payload materialization is deferred until callback time on the direct-`Pattern` wrong-text-model rows.
- Do not broaden into the surrounding keyword-error, success, compile-contract, or validation sections except for minimal mechanical renames needed to keep the shared wrong-text-model contract tests wired up.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model'`
- `bash -lc "! rg -n 'def _pattern_helper_collection_replacement_wrong_text_model_manifest_payload\\(|def _pattern_helper_collection_replacement_wrong_text_model_workloads\\(|def _pattern_helper_collection_replacement_wrong_text_model_manifest\\(|def _assert_pattern_helper_collection_replacement_wrong_text_model_payload_round_trip\\(|def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_result\\(|def _pattern_helper_collection_replacement_wrong_text_model_expected_build_calls\\(|def _pattern_helper_collection_replacement_wrong_text_model_expected_callback_call\\(|def _run_cpython_pattern_helper_collection_replacement_wrong_text_model_workload\\(|def _assert_compiled_pattern_module_helper_wrong_text_model_payload_round_trip\\(|def _compiled_pattern_module_helper_wrong_text_model_expected_callback_result\\(|def _compiled_pattern_module_helper_wrong_text_model_expected_callback_call\\(|def _run_cpython_compiled_pattern_module_helper_wrong_text_model_workload\\(|test_standard_benchmark_manifest_preserves_pattern_collection_replacement_wrong_text_model_rows_until_helper_invocation|test_run_internal_workload_probe_measures_pattern_helper_collection_replacement_wrong_text_model_workloads|test_pattern_helper_collection_replacement_wrong_text_model_callbacks_precompile_before_timing|test_standard_benchmark_manifest_preserves_compiled_pattern_module_wrong_text_model_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_wrong_text_model_workloads|test_compiled_pattern_module_wrong_text_model_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    MODULE_BOUNDARY_MANIFEST_PATH,
    _is_collection_replacement_pattern_wrong_text_model_workload,
    _is_collection_replacement_wrong_text_model_workload,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _selected_manifest_workloads,
)

collection_ids = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_wrong_text_model_workload,
    )
)
boundary_ids = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
    )
)
pattern_ids = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
    )
)

assert collection_ids == (
    "module-split-on-bytes-string-purged-str-compiled-pattern",
    "module-findall-on-str-string-purged-bytes-compiled-pattern",
    "module-finditer-on-bytes-string-warm-str-compiled-pattern",
    "module-sub-on-bytes-string-warm-str-compiled-pattern",
    "module-subn-on-str-string-purged-bytes-compiled-pattern",
)
assert boundary_ids == (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)
assert pattern_ids == (
    "pattern-split-on-bytes-string-warm-str",
    "pattern-sub-on-bytes-string-warm-str",
    "pattern-subn-on-str-string-purged-bytes",
)

print("ok", len(collection_ids), len(boundary_ids), len(pattern_ids))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or any non-benchmark test file in this run.
- Prefer deleting duplicate contract plumbing over introducing another detached id-keyed helper layer.

## Notes
- `RBR-0960` is the next available task id in the current checkout:
  - `rg -n 'RBR-0960|RBR-0961|RBR-0962|RBR-0963|RBR-0964' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0959-publish-pattern-replacement-count-alias-keyword-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model'` currently passes (`39 passed, 593 deselected`);
  - the selector probe in Verification currently passes (`ok 5 3 3`), proving the three live wrong-text-model surfaces already exist directly on the tracked manifest-selected workload paths; and
  - the negative `rg` check in Verification currently fails because the duplicated helper/test names named in this task are still present in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, which is the exact cleanup this task queues.
