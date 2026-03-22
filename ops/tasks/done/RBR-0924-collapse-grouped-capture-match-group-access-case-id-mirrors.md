# RBR-0924: Collapse grouped-capture match-group-access case-id mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining detached grouped-capture subset mirrors from `tests/python/test_grouped_capture_parity_suite.py` so the suite derives both its leading-capture slice and its match-group-access slice directly from the live owner bundles it already loads instead of caching second copies of those case ids.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` no longer defines these detached case-id mirrors:
  - `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER`
  - `GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS`
  - `MATCH_GROUP_ACCESS_CASE_IDS`
- Keep the grouped-capture subset surfaces live and file-local rather than replacing the deleted mirrors with another detached tuple/list/set/map:
  - `GROUPED_SEGMENT_LEADING_CAPTURE_CASES` remains available, but it is derived directly from `GROUPED_SEGMENT_FIXTURE_BUNDLE.cases`;
  - `MATCH_GROUP_ACCESS_CASES` remains available, but it is derived directly from the existing grouped-capture bundle constants already loaded in this file; and
  - if helpers remain, keep them as tiny owner-local live selectors over the bundle `cases`, not a new shared support module, registry table, or cached id mirror.
- Preserve the current leading-capture subset exactly while routing it through the live grouped-segment bundle:
  - `GROUPED_SEGMENT_LEADING_CAPTURE_CASES` still resolves, in order, to `grouped-segment-leading-capture-module-search-str` then `grouped-segment-leading-capture-pattern-search-str`;
  - `test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier()` still proves those two rows remain on the direct parity frontier and remain disjoint from the supplemental miss cases; and
  - do not add, drop, or reorder leading-capture rows while deleting the mirrors.
- Preserve the current grouped-capture match-group-access surface exactly while routing it through live bundle selectors:
  - `MATCH_GROUP_ACCESS_CASES` still spans the same 32 ordered rows it covers today;
  - `test_match_group_access_rows_remain_on_grouped_capture_fixture_paths()` still proves that same ordered surface; and
  - do not add, drop, or reorder any of those 32 rows while deleting the mirrors.
- Keep this cleanup structural only:
  - do not change `REGS_PARITY_CASE_IDS`, `SUPPLEMENTAL_MISS_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, compile/match behavior, fixture contents, benchmark/report outputs, or tracked project-state prose; and
  - do not widen into `tests/python/fixture_parity_support.py`, fixture manifest edits, or unrelated parity suites in this run.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `bash -lc "! rg -n '^(GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER|GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS|MATCH_GROUP_ACCESS_CASE_IDS)\\s*=' tests/python/test_grouped_capture_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_grouped_capture_parity_suite import (
    GROUPED_MATCH_FIXTURE_BUNDLE,
    GROUPED_SEGMENT_FIXTURE_BUNDLE,
    GROUPED_ALTERNATION_FIXTURE_BUNDLE,
    NAMED_GROUP_FIXTURE_BUNDLE,
    OPTIONAL_GROUP_FIXTURE_BUNDLE,
    OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE,
    NESTED_GROUP_FIXTURE_BUNDLE,
    NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE,
    GROUPED_SEGMENT_LEADING_CAPTURE_CASES,
    MATCH_GROUP_ACCESS_CASES,
)

leading_capture_live = tuple(
    case.case_id
    for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
    if "leading-capture" in case.case_id
)
assert leading_capture_live == (
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-leading-capture-pattern-search-str",
)
assert tuple(case.case_id for case in GROUPED_SEGMENT_LEADING_CAPTURE_CASES) == leading_capture_live

match_group_access_live = (
    tuple(case.case_id for case in GROUPED_MATCH_FIXTURE_BUNDLE.cases[:4])
    + tuple(
        case.case_id
        for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
        if case.case_id.startswith("grouped-segment-") and case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
        if case.case_id.startswith("grouped-alternation-")
        and case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in NAMED_GROUP_FIXTURE_BUNDLE.cases
        if case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
        if case.case_id.startswith("named-grouped-segment-")
        and case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
        if case.case_id.startswith("named-grouped-alternation-")
        and case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in OPTIONAL_GROUP_FIXTURE_BUNDLE.cases
        if case.case_id.startswith("systematic-optional-group-")
        and "-absent-" in case.case_id
    )
    + tuple(
        case.case_id
        for case in OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
        if case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in NESTED_GROUP_FIXTURE_BUNDLE.cases
        if case.operation != "compile"
    )
    + tuple(
        case.case_id
        for case in NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
        if case.operation != "compile"
    )
)
assert match_group_access_live == (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-segment-module-search-str",
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-pattern-fullmatch-str",
    "grouped-segment-leading-capture-pattern-search-str",
    "grouped-alternation-module-search-str",
    "grouped-alternation-pattern-fullmatch-str",
    "named-group-module-search-metadata-str",
    "named-group-pattern-search-metadata-str",
    "named-grouped-segment-module-search-str",
    "named-grouped-segment-pattern-fullmatch-str",
    "named-grouped-alternation-module-search-str",
    "named-grouped-alternation-pattern-fullmatch-str",
    "systematic-optional-group-numbered-module-search-absent-str",
    "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
    "systematic-optional-group-named-module-search-absent-str",
    "systematic-optional-group-named-pattern-fullmatch-absent-str",
    "optional-group-alternation-module-search-present-str",
    "optional-group-alternation-pattern-fullmatch-absent-str",
    "named-optional-group-alternation-module-search-present-str",
    "named-optional-group-alternation-pattern-fullmatch-absent-str",
    "nested-group-module-search-str",
    "nested-group-pattern-fullmatch-str",
    "named-nested-group-module-search-str",
    "named-nested-group-pattern-fullmatch-str",
    "nested-group-alternation-module-search-str",
    "nested-group-alternation-pattern-fullmatch-str",
    "named-nested-group-alternation-module-search-str",
    "named-nested-group-alternation-pattern-fullmatch-str",
)
assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == match_group_access_live
print("ok", len(leading_capture_live), len(match_group_access_live))
PY`

## Constraints
- Keep the change limited to `tests/python/test_grouped_capture_parity_suite.py`. Do not edit fixture manifests, shared parity-support helpers, harness modules, reports, README copy, or tracked state files in this run.
- Preserve the grouped-capture subset order and coverage exactly. The point is to delete one more owner-local representation layer, not to reinterpret which grouped-capture rows receive match-group-access or leading-capture coverage.

## Notes
- `RBR-0924` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0924|RBR-0925|RBR-0926|RBR-0927|RBR-0928|RBR-0929|RBR-0930' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0924`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`432 passed in 0.31s`);
  - `rg -n '^(GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER|GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS|MATCH_GROUP_ACCESS_CASE_IDS)\\s*=' tests/python/test_grouped_capture_parity_suite.py` currently finds the remaining mirrors at lines `34`, `38`, and `260`; and
  - the task-local live-selector probe in Acceptance currently passes (`ok 2 32`), proving the suite's existing owner bundles already recover the same leading-capture pair and ordered 32-row match-group-access surface without those cached mirrors.

## Completion
- 2026-03-22: Removed the three detached case-id mirrors from `tests/python/test_grouped_capture_parity_suite.py` and rebuilt `GROUPED_SEGMENT_LEADING_CAPTURE_CASES` plus `MATCH_GROUP_ACCESS_CASES` directly from the live grouped-capture fixture bundles without changing their ordered surfaces.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`, the mirror-name grep check, and the task-local live-selector probe (`ok 2 32`).
