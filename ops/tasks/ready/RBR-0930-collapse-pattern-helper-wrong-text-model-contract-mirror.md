# RBR-0930: Collapse pattern-helper wrong-text-model contract mirror

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the benchmark-test-only `PatternHelperCollectionReplacementWrongTextModelCase` / `PATTERN_HELPER_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CASES` mirror from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the pattern-helper collection/replacement wrong-text-model contract section derives its three-row surface directly from the tracked `benchmarks/workloads/collection_replacement_boundary.py` manifest it already validates instead of maintaining a second handwritten copy of those rows.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these detached mirror structures:
  - `class PatternHelperCollectionReplacementWrongTextModelCase`
  - `PATTERN_HELPER_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CASES`
- Replace that mirror layer with tiny file-local live selectors or projections over the tracked collection/replacement manifest:
  - use `COLLECTION_REPLACEMENT_MANIFEST_PATH` plus existing file-local workload-loading helpers such as `_selected_manifest_workloads(...)`, `_manifest_workloads(...)`, or `_manifest_workloads_by_id(...)`;
  - do not add a new shared helper module, registry table, or another detached tuple/list/dict that restates the same three rows; and
  - keep any replacement helpers local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Preserve the current wrong-text-model workload surface exactly while routing it through the tracked manifest:
  - the selected workload ids still resolve, in order, to `pattern-split-on-bytes-string-warm-str`, `pattern-sub-on-bytes-string-warm-str`, then `pattern-subn-on-str-string-purged-bytes`;
  - the manifest-contract tests still write the same `-contract` workload ids in that order;
  - the anchor contract still resolves those `-contract` ids to `workflow-pattern-split-str-pattern-on-bytes-string`, `workflow-pattern-sub-str-pattern-on-bytes-string`, and `workflow-pattern-subn-bytes-pattern-on-str-string`; and
  - the payload round-trip checks still prove `use_compiled_pattern is False`, the same `haystack_text_model` values, the same `expected_exception` payloads, and the same text-vs-bytes payload typing.
- Keep the callback/precompile coverage anchored to the same behavior:
  - `test_pattern_helper_collection_replacement_wrong_text_model_callbacks_precompile_before_timing(...)` still proves the same build calls and callback calls for the three rows:
    - `pattern-split-on-bytes-string-warm-str`: build calls `[("compile", "abc", 0)]`, callback call `("pattern.split", b"zabczz", (0,), {})`;
    - `pattern-sub-on-bytes-string-warm-str`: build calls `[("compile", "abc", 0)]`, callback call `("pattern.sub", "x", b"zabczz", (0,), {})`; and
    - `pattern-subn-on-str-string-purged-bytes`: build calls `[("compile", b"abc", 0), ("purge",)]`, callback call `("pattern.subn", b"x", "zabczz", (0,), {})`.
- Keep this cleanup structural only:
  - do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, correctness fixtures, reports, README/current-status/backlog prose, or other benchmark-contract sections in this run; and
  - keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_helper_collection_replacement_wrong_text_model or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured'`
  - `bash -lc "! rg -n '^(class PatternHelperCollectionReplacementWrongTextModelCase|PATTERN_HELPER_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    _is_collection_replacement_pattern_wrong_text_model_workload,
    _selected_manifest_workloads,
)

tracked = tuple(
    workload.workload_id
    for workload in _selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
    )
)
assert tracked == (
    "pattern-split-on-bytes-string-warm-str",
    "pattern-sub-on-bytes-string-warm-str",
    "pattern-subn-on-str-string-purged-bytes",
)
print("ok", len(tracked))
PY`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into tracked workload edits, harness-module refactors, fixture changes, or feature work.
- Preserve the current three-row benchmark contract exactly. The point is to delete one benchmark-owner mirror layer, not to reinterpret which collection/replacement wrong-text-model rows stay on the shared benchmark surface.

## Notes
- `RBR-0930` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0930|RBR-0931|RBR-0932|RBR-0933|RBR-0934|RBR-0935' ops/state/backlog.md ops/state/current_status.md || true` returned no reserved follow-on ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0929-catch-up-pattern-collection-replacement-wrong-text-model-boundary-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_helper_collection_replacement_wrong_text_model or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured'` currently passes (`14 passed, 567 deselected, 3 subtests passed in 0.28s`);
  - `rg -n '^(class PatternHelperCollectionReplacementWrongTextModelCase|PATTERN_HELPER_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CASES)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently finds the remaining mirror at lines `12349` and `12363`; and
  - the task-local tracked-manifest probe in Acceptance currently passes (`ok 3`), proving the three-row surface already exists in the tracked benchmark workload manifest without the extra benchmark-test case table.
