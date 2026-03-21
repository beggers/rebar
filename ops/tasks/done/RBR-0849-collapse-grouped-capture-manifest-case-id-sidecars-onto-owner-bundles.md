# RBR-0849: Collapse grouped-capture manifest case-id sidecars onto owner bundles

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the grouped-capture parity suite's remaining full-manifest case-id sidecars from `tests/python/test_grouped_capture_parity_suite.py` so the loaded owner bundles become the sole canonical source for those manifest-wide published case sets.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` stops defining or reading these detached manifest-wide case-id mirrors:
  - `GROUPED_MATCH_TRACKED_CASE_IDS`
  - `NAMED_GROUP_CASE_IDS`
  - `GROUPED_SEGMENT_CASE_IDS`
  - `GROUPED_ALTERNATION_CASE_IDS`
  - `OPTIONAL_GROUP_CASE_IDS`
  - `OPTIONAL_GROUP_ALTERNATION_CASE_IDS`
  - `NESTED_GROUP_CASE_IDS`
  - `NESTED_GROUP_ALTERNATION_CASE_IDS`
  - `GROUPED_CAPTURE_TRACKED_CASE_IDS`
- The grouped-capture owner derives those manifest-wide published case ids directly from the already-loaded owner bundles instead of restating them in top-level tuples:
  - `_grouped_capture_direct_test_case_id_buckets()`
  - `_grouped_match_frontier_contract_case_ids()`
  - `test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier()`
  - `test_grouped_capture_parity_suite_tracks_published_case_frontier()`
  - `test_grouped_capture_direct_test_buckets_cover_selected_frontier()`
- Preserve the current effective published behavior exactly while deleting the mirrors:
  - the owner-bundle manifest order still resolves to `grouped-match-workflows`, `named-group-workflows`, `grouped-segment-workflows`, `nested-group-workflows`, `nested-group-alternation-workflows`, `grouped-alternation-workflows`, `optional-group-workflows`, and `optional-group-alternation-workflows`;
  - `_grouped_capture_direct_test_case_id_buckets()` still exposes the same eight keys in the same order: `grouped-match`, `named-group`, `grouped-segment`, `grouped-alternation`, `optional-group`, `optional-group-alternation`, `nested-group`, and `nested-group-alternation`;
  - `_grouped_match_frontier_contract_case_ids()` still returns selected case ids `("grouped-module-fullmatch-two-capture-gap-str", "grouped-pattern-fullmatch-two-capture-gap-str")` and uncovered case ids `("grouped-module-search-single-capture-str", "grouped-module-fullmatch-single-capture-str", "grouped-pattern-search-single-capture-str", "grouped-pattern-match-single-capture-str")`; and
  - the grouped-segment leading-capture subset and the match-group accessor subset stay in their current order and coverage.
- Keep the explicit non-mirror subset contracts unchanged:
  - do not change `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER`, `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, `REGS_PARITY_CASE_IDS`, `SUPPLEMENTAL_MISS_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, compile/match behavior, or the grouped-match selected-vs-uncovered frontier split beyond deriving it from the bundle data already loaded in this file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `bash -lc "! rg -n '^(GROUPED_MATCH_TRACKED_CASE_IDS|NAMED_GROUP_CASE_IDS|GROUPED_SEGMENT_CASE_IDS|GROUPED_ALTERNATION_CASE_IDS|OPTIONAL_GROUP_CASE_IDS|OPTIONAL_GROUP_ALTERNATION_CASE_IDS|NESTED_GROUP_CASE_IDS|NESTED_GROUP_ALTERNATION_CASE_IDS|GROUPED_CAPTURE_TRACKED_CASE_IDS) =' tests/python/test_grouped_capture_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_grouped_capture_parity_suite as mod

bundle_case_ids = {
    bundle.expected_manifest_id: tuple(case.case_id for case in bundle.cases)
    for bundle in mod.FIXTURE_BUNDLES
}
assert mod._grouped_capture_direct_test_case_id_buckets() == {
    "grouped-match": frozenset(bundle_case_ids["grouped-match-workflows"]),
    "named-group": frozenset(bundle_case_ids["named-group-workflows"]),
    "grouped-segment": frozenset(bundle_case_ids["grouped-segment-workflows"]),
    "grouped-alternation": frozenset(bundle_case_ids["grouped-alternation-workflows"]),
    "optional-group": frozenset(bundle_case_ids["optional-group-workflows"]),
    "optional-group-alternation": frozenset(
        bundle_case_ids["optional-group-alternation-workflows"]
    ),
    "nested-group": frozenset(bundle_case_ids["nested-group-workflows"]),
    "nested-group-alternation": frozenset(
        bundle_case_ids["nested-group-alternation-workflows"]
    ),
}
selected_case_ids, uncovered_case_ids = mod._grouped_match_frontier_contract_case_ids()
assert selected_case_ids == (
    "grouped-module-fullmatch-two-capture-gap-str",
    "grouped-pattern-fullmatch-two-capture-gap-str",
)
assert uncovered_case_ids == (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
)
assert tuple(case.case_id for case in mod.GROUPED_SEGMENT_LEADING_CAPTURE_CASES) == (
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-leading-capture-pattern-search-str",
)
assert tuple(case.case_id for case in mod.MATCH_GROUP_ACCESS_CASES[:6]) == (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-segment-module-search-str",
    "grouped-segment-leading-capture-module-search-str",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored ownership layer inside the grouped-capture parity owner, not to reinterpret grouped-capture semantics, narrow or widen the published frontier, or introduce another shared helper layer.
- Keep scope limited to `tests/python/test_grouped_capture_parity_suite.py`. Do not edit correctness fixtures, selector registry code, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0849` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0848`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0849`.
- No blocked architecture task exists to reopen first, and the current queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`432 passed in 0.32s`);
  - a live probe in this run confirmed that each manifest-wide tracked tuple currently matches the loaded bundle rows exactly for `grouped-match`, `named-group`, `grouped-segment`, `grouped-alternation`, `optional-group`, `optional-group-alternation`, `nested-group`, and `nested-group-alternation`;
  - the task-local probe in Acceptance already passes in the current checkout except for the absence check; and
  - `bash -lc "! rg -n '^(GROUPED_MATCH_TRACKED_CASE_IDS|NAMED_GROUP_CASE_IDS|GROUPED_SEGMENT_CASE_IDS|GROUPED_ALTERNATION_CASE_IDS|OPTIONAL_GROUP_CASE_IDS|OPTIONAL_GROUP_ALTERNATION_CASE_IDS|NESTED_GROUP_CASE_IDS|NESTED_GROUP_ALTERNATION_CASE_IDS|GROUPED_CAPTURE_TRACKED_CASE_IDS) =' tests/python/test_grouped_capture_parity_suite.py"` currently fails exactly on this cleanup because those mirrored top-level tuples still exist.
- This is the direct post-JSON follow-on to the grouped-capture owner cleanup track rather than a new harness direction:
  - `RBR-0817` already moved the suite onto the shared `GROUPED_CAPTURE_FIXTURE_SELECTOR`; and
  - `RBR-0589` already reduced grouped-capture frontier plumbing to the grouped-match exception plus live bundle rows, leaving these remaining full-manifest case-id mirrors as the next small deletion.

## Completion
- 2026-03-21: Removed the detached grouped-capture manifest-wide case-id mirrors from `tests/python/test_grouped_capture_parity_suite.py`.
- Added bundle-local case-id selectors and direct-test bundle ordering that derive grouped-match, named-group, grouped-segment, grouped-alternation, optional-group, optional-group-alternation, nested-group, and nested-group-alternation coverage directly from the already loaded owner bundles without changing subset contracts.
- Rewired `_grouped_capture_direct_test_case_id_buckets()`, `_grouped_match_frontier_contract_case_ids()`, `test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier()`, `test_grouped_capture_parity_suite_tracks_published_case_frontier()`, and `test_grouped_capture_direct_test_buckets_cover_selected_frontier()` to use bundle-derived case ids while leaving `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER`, `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, `REGS_PARITY_CASE_IDS`, `SUPPLEMENTAL_MISS_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, and `PATTERN_BOUNDS_NO_MATCH_CASES` unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` (`432 passed in 0.34s`), `bash -lc "! rg -n '^(GROUPED_MATCH_TRACKED_CASE_IDS|NAMED_GROUP_CASE_IDS|GROUPED_SEGMENT_CASE_IDS|GROUPED_ALTERNATION_CASE_IDS|OPTIONAL_GROUP_CASE_IDS|OPTIONAL_GROUP_ALTERNATION_CASE_IDS|NESTED_GROUP_CASE_IDS|NESTED_GROUP_ALTERNATION_CASE_IDS|GROUPED_CAPTURE_TRACKED_CASE_IDS) =' tests/python/test_grouped_capture_parity_suite.py"` (passes with no matches), and the task-local import/order probe from Acceptance (`ok`).
