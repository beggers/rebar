# RBR-0950: Collapse compiled-pattern wrong-text-model owner-path duplicates

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the parallel collection-replacement versus module-boundary wrapper/test copies from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern wrong-text-model benchmark contract runs through one file-local owner-spec path instead of maintaining paired source selectors, paired workload wrappers, and paired test bodies that only differ by manifest metadata and expected workload ids.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on these duplicated owner-path wrappers:
  - `def _compiled_pattern_module_helper_wrong_text_model_workload(...)`
  - `def _compiled_pattern_module_boundary_wrong_text_model_workload(...)`
  - `def _compiled_pattern_module_helper_wrong_text_model_source_workloads(...)`
  - `def _compiled_pattern_module_boundary_wrong_text_model_source_workloads(...)`
- Replace those wrappers with one file-local owner-spec surface that is small and explicit enough to keep the contract legible without introducing a new shared module, registry, or checked-in data layer:
  - it may be a tiny tuple of two specs, a frozen dataclass pair, or equivalent file-local metadata;
  - each spec must carry only the metadata that actually differs between the two owner paths: the manifest selector, contract manifest id, note-surface label, contract filename stem, and expected source workload ids; and
  - the live source workloads must still come directly from `_selected_manifest_workloads(...)` against the tracked manifests rather than another handwritten workload builder.
- Preserve the current bounded source surfaces exactly:
  - the collection/replacement owner path still resolves, in order, to:
    - `module-split-on-bytes-string-purged-str-compiled-pattern`
    - `module-findall-on-str-string-purged-bytes-compiled-pattern`
    - `module-finditer-on-bytes-string-warm-str-compiled-pattern`
    - `module-sub-on-bytes-string-warm-str-compiled-pattern`
    - `module-subn-on-str-string-purged-bytes-compiled-pattern`
  - the module-boundary owner path still resolves, in order, to:
    - `module-search-on-bytes-string-warm-str-compiled-pattern`
    - `module-match-on-str-string-purged-bytes-compiled-pattern`
    - `module-fullmatch-on-bytes-string-warm-str-compiled-pattern`
  - the generated contract workloads still use those same ids with `-contract` suffixes in the same per-owner order;
  - the collection/replacement owner path still uses manifest id `collection-replacement-boundary` with note surface `collection/replacement`; and
  - the module-boundary owner path still uses manifest id `module-boundary` with note surface `module-boundary`.
- Collapse the paired test bodies onto one owner-spec-driven structure while preserving behavior:
  - the two `test_standard_benchmark_manifest_preserves_...wrong_text_model_rows_until_helper_invocation(...)` copies become one parametrized or equivalently shared owner-spec test body;
  - the two `test_run_internal_workload_probe_measures_...wrong_text_model_workloads(...)` copies become one parametrized or equivalently shared owner-spec test body; and
  - the two `test_compiled_pattern_module_...wrong_text_model_callbacks_precompile_first_argument_before_timing(...)` copies become one parametrized or equivalently shared owner-spec test body.
- The shared owner-spec-driven tests must continue proving the same contract for both owner paths:
  - manifest payload round-trip checks still preserve `use_compiled_pattern is True`, the same `haystack_text_model`, the same `expected_exception`, and the same `str` versus `bytes` payload typing;
  - the manifest-preservation path still compares exact CPython `TypeError` text against `run_benchmark_workload_with_cpython(...)`;
  - the internal-probe path still measures both adapters on all eight rows and still requires `probe["status"] == "measured"` plus `probe["median_ns"] > 0`; and
  - the precompile-first callback path still uses `_compiled_pattern_module_helper_wrong_text_model_expected_build_calls(...)`, `_compiled_pattern_module_helper_wrong_text_model_expected_callback_call(...)`, and `_compiled_pattern_module_helper_wrong_text_model_expected_callback_result(...)` to prove the same compiled-pattern-first-argument behavior before helper invocation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_wrong_text_model_workload\\(|def _compiled_pattern_module_boundary_wrong_text_model_workload\\(|def _compiled_pattern_module_helper_wrong_text_model_source_workloads\\(|def _compiled_pattern_module_boundary_wrong_text_model_source_workloads\\(|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_wrong_text_model_rows_until_helper_invocation|test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_wrong_text_model_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_wrong_text_model_workloads|test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_wrong_text_model_workloads|test_compiled_pattern_module_helper_wrong_text_model_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_boundary_wrong_text_model_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    MODULE_BOUNDARY_MANIFEST_PATH,
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

print("ok", len(collection_ids), len(boundary_ids))
PY`

## Constraints
- Keep the cleanup structural and limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/module_boundary.py`, `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or any non-benchmark test file in this run.
- Prefer deleting duplicate wrappers and test bodies over introducing another detached id-keyed helper layer.

## Notes
- `RBR-0950` is the next available task id in the current checkout:
  - `rg -n 'RBR-0950|RBR-0951|RBR-0952|RBR-0953|RBR-0954' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 16` currently ends at `RBR-0949-catch-up-pattern-search-bytes-endpos-keyword-indexlike-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The shared-ready-queue stall rule does not apply in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model'` currently passes (`25 passed, 591 deselected`);
  - `bash -lc "rg -n 'def _compiled_pattern_module_helper_wrong_text_model_workload\\(|def _compiled_pattern_module_boundary_wrong_text_model_workload\\(|def _compiled_pattern_module_helper_wrong_text_model_source_workloads\\(|def _compiled_pattern_module_boundary_wrong_text_model_source_workloads\\(|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_wrong_text_model_rows_until_helper_invocation|test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_wrong_text_model_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_wrong_text_model_workloads|test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_wrong_text_model_workloads|test_compiled_pattern_module_helper_wrong_text_model_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_boundary_wrong_text_model_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently finds the paired wrappers and six duplicate test bodies at lines `15875`, `15885`, `15919`, `15926`, `16072`, `16130`, `16200`, `16239`, `16273`, and `16313`; and
  - the selector probe in Verification currently passes (`ok 5 3`), proving both owner surfaces already exist directly in the tracked manifests without the extra wrapper/test duplication.

## Completion Note
- Landed a file-local `CompiledPatternModuleWrongTextModelOwnerSpec` pair in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, deleted the four owner-path duplicate workload/source selectors, and collapsed the manifest, internal-probe, and precompile-first callback checks onto shared owner-spec-driven tests while preserving the published 5-row collection/replacement path and 3-row module-boundary path exactly.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_wrong_text_model or compiled_pattern_module_boundary_wrong_text_model'` (`26 passed, 590 deselected`)
  - `bash -lc "! rg -n 'def _compiled_pattern_module_helper_wrong_text_model_workload\\(|def _compiled_pattern_module_boundary_wrong_text_model_workload\\(|def _compiled_pattern_module_helper_wrong_text_model_source_workloads\\(|def _compiled_pattern_module_boundary_wrong_text_model_source_workloads\\(|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_wrong_text_model_rows_until_helper_invocation|test_standard_benchmark_manifest_preserves_compiled_pattern_module_boundary_wrong_text_model_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_wrong_text_model_workloads|test_run_internal_workload_probe_measures_compiled_pattern_module_boundary_wrong_text_model_workloads|test_compiled_pattern_module_helper_wrong_text_model_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_boundary_wrong_text_model_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - the selector probe from Verification (`ok 5 3`)
