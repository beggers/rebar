# RBR-0861: Collapse pattern-boundary window workload-id mirrors onto live selectors

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the remaining pattern-boundary workload-id mirror frozensets from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` where the live benchmark rows already carry enough structure to identify the same keyword-window and positional-indexlike slices.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops defining or reading these detached workload-id mirrors:
  - `PATTERN_WINDOW_POSITIONAL_INDEXLIKE_WORKLOAD_IDS`
  - `PATTERN_KEYWORD_WINDOW_CARRIER_WORKLOAD_IDS`
- The existing pattern-boundary selectors and signature helpers derive the same bounded slices directly from live workload structure instead of top-level workload-id tables:
  - `_is_pattern_window_positional_indexlike_workload(...)`
  - `_pattern_window_positional_indexlike_workload_signature(...)`
  - `_is_pattern_keyword_window_workload(...)`
  - `_pattern_keyword_window_workload_signature(...)`
- Keep the pattern-boundary measured-row coverage unchanged while deleting those mirrors:
  - `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured`
  This assertion should source its ordered keyword and positional workload ids from `source_tree_combined_case("pattern-boundary").target_manifest.workloads` through the shared live selectors instead of a handwritten 10-id tuple literal.
- Preserve the current pattern-boundary benchmark surface exactly after the refactor:
  - keep the keyword-window slice ordered as `pattern-search-pos-keyword-warm-str`, `pattern-match-pos-keyword-purged-str`, `pattern-fullmatch-window-keyword-purged-bytes`, `pattern-findall-bool-window-keyword-warm-str`, and `pattern-finditer-window-indexlike-purged-bytes`;
  - keep the positional-indexlike slice ordered as `pattern-search-pos-indexlike-positional-warm-str`, `pattern-search-endpos-indexlike-positional-purged-bytes`, `pattern-fullmatch-window-indexlike-positional-purged-bytes`, `pattern-findall-window-indexlike-positional-warm-str`, and `pattern-finditer-window-indexlike-positional-purged-bytes`;
  - keep the current anchor-contract expectations, callback-result parity checks, and zero-gap manifest counts behaviorally unchanged; and
  - do not widen into additional `pattern-boundary` rows, new manifest selectors, or another benchmark-helper layer in this run.
- Do not broaden scope beyond this mirror deletion:
  - do not change benchmark manifests, harness modules, reports, correctness fixtures, README copy, or tracked project-state prose; and
  - do not retune pattern-window keyword semantics, positional-indexlike argument materialization, or published benchmark counts in this run.
- Verification passes with:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or (pattern-window-positional-indexlike or pattern-window-keyword)'`
  - `bash -lc "! rg -n '^(PATTERN_WINDOW_POSITIONAL_INDEXLIKE_WORKLOAD_IDS|PATTERN_KEYWORD_WINDOW_CARRIER_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.benchmarks.test_source_tree_combined_boundary_benchmarks as mod

manifest = mod.source_tree_combined_case("pattern-boundary").target_manifest
keyword_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if mod._is_pattern_keyword_window_workload(workload)
)
positional_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if mod._is_pattern_window_positional_indexlike_workload(workload)
)

assert keyword_ids == (
    "pattern-search-pos-keyword-warm-str",
    "pattern-match-pos-keyword-purged-str",
    "pattern-fullmatch-window-keyword-purged-bytes",
    "pattern-findall-bool-window-keyword-warm-str",
    "pattern-finditer-window-indexlike-purged-bytes",
)
assert positional_ids == (
    "pattern-search-pos-indexlike-positional-warm-str",
    "pattern-search-endpos-indexlike-positional-purged-bytes",
    "pattern-fullmatch-window-indexlike-positional-purged-bytes",
    "pattern-findall-window-indexlike-positional-warm-str",
    "pattern-finditer-window-indexlike-positional-purged-bytes",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the duplicated pattern-boundary workload-id mirrors inside the combined benchmark test owner, not to reinterpret keyword-window semantics, broaden the manifest, or introduce another shared abstraction.
- Keep scope limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Notes
- `RBR-0861` is the next available architecture task id in the current checkout:
  - `RBR-0860` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0861`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or (pattern-window-positional-indexlike or pattern-window-keyword)'` currently passes (`9 passed, 327 deselected in 0.20s`);
  - the task-local selector-order probe in Acceptance already passes in the current checkout (`ok`), confirming that the live pattern-boundary rows already expose the exact five keyword-window ids and five positional-indexlike ids without the top-level frozensets; and
  - `bash -lc "! rg -n '^(PATTERN_WINDOW_POSITIONAL_INDEXLIKE_WORKLOAD_IDS|PATTERN_KEYWORD_WINDOW_CARRIER_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails exactly on this cleanup because those mirrored frozensets still exist.
- This stays on the same post-JSON benchmark-harness simplification track as the recent mirror removals in the same owner file:
  - `RBR-0859` already collapsed the adjacent collection-replacement workload-id mirrors onto live selectors; and
  - this follow-on only removes the remaining pattern-boundary window mirrors without opening a new architecture lane.
