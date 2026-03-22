# RBR-0907: Collapse the grouped-replacement collection selector mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the detached `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS` tuple from `tests/python/test_fixture_backed_replacement_parity_suite.py`, so the grouped-replacement owner derives its two-row collection subset directly from the canonical `collection-replacement-workflows` bundle it already loads instead of maintaining a second handwritten selector list.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines or reads `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS`:
  - delete the top-level tuple instead of replacing it with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live selector over the loaded collection bundle rows rather than another cached selector mirror.
- Route the grouped-replacement collection subset through live owner data instead of the deleted mirror:
  - `_load_surface(...)` still builds the adjusted `collection-replacement-workflows` bundle for `GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID`, but it derives the selected case ids from the loaded collection bundle rows rather than from a handwritten tuple;
  - preserve the current selected collection order exactly as `module-sub-callable-str`, then `module-sub-grouping-template`;
  - keep `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, `GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID`, and `_expected_selected_replacement_case_ids(...)` behaviorally unchanged apart from sourcing that collection subset through the live bundle path; and
  - keep `GROUPED_TEMPLATE_CALLABLE_CASE_ID` and `GROUPED_TEMPLATE_SELECTED_CASE_ID` available for the direct targeted assertions that still need those two specific ids.
- Rewire the current owner-path checks through that live selector instead of the deleted mirror:
  - `test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit()`;
  - `test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures()`; and
  - any other reads of `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS` in `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change fixture contents, the grouped-replacement bundle order, compile-pattern coverage, match-group-access coverage, template-expand coverage, pending-bytes routing, replacement semantics, benchmark/report outputs, or tracked project-state prose; and
  - do not widen into the grouped-replacement counter contracts, shared parity-support helpers, or new selector registries in this run.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^GROUPED_REPLACEMENT_COLLECTION_CASE_IDS = ' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles, published_fixture_bundles_by_manifest_id
from rebar_harness.correctness import GROUPED_REPLACEMENT_FIXTURE_SELECTOR, select_correctness_fixture_paths
import tests.python.test_fixture_backed_replacement_parity_suite as mod

bundles = load_published_fixture_bundles(
    select_correctness_fixture_paths(GROUPED_REPLACEMENT_FIXTURE_SELECTOR),
    pattern_extractor=case_pattern,
)
collection_bundle = published_fixture_bundles_by_manifest_id(bundles)[
    "collection-replacement-workflows"
]
selected_case_ids = tuple(
    case.case_id
    for case in collection_bundle.cases
    if case.family == "grouped_template_replacement_workflow"
    or "callable-replacement" in case.categories
)
assert selected_case_ids == (
    "module-sub-callable-str",
    "module-sub-grouping-template",
)
surface_bundle = mod.GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
    mod.GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID
]
assert tuple(case.case_id for case in surface_bundle.cases) == selected_case_ids
print("ok")
PY`

## Constraints
- Keep the change limited to `tests/python/test_fixture_backed_replacement_parity_suite.py`. Do not widen into fixture rewrites, grouped-replacement publication changes, benchmark work, or harness-module refactors in this run.
- Preserve the current two-row grouped collection subset exactly; the point is to delete one owner-local selector mirror, not to reinterpret which collection rows belong to the grouped replacement surface.

## Notes
- `RBR-0907` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0907' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on id; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0907'` returned no existing task file.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1226 passed in 0.88s`);
  - `bash -lc "! rg -n '^GROUPED_REPLACEMENT_COLLECTION_CASE_IDS = ' tests/python/test_fixture_backed_replacement_parity_suite.py"` currently fails exactly on the remaining mirror at line `107`; and
  - the task-local probe in Acceptance already passes (`ok`), confirming the canonical `collection-replacement-workflows` owner rows can recover the same ordered two-case subset that the grouped-replacement surface currently selects.
- This stays on the same post-JSON parity-harness simplification track as the recent owner-path cleanup in the same file:
  - `RBR-0857` already removed the remaining named/nested/wider-ranged replacement case-id mirrors while explicitly leaving this collection subset tuple in place because the owner still needed a bounded subset carve-out; and
  - the live collection bundle now has a direct family/category path for that exact two-case carve-out, so this tuple is the next bounded mirror to delete without changing the grouped replacement frontier.

## Completion
- Removed the `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS` tuple from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Added `_grouped_replacement_collection_case_ids(...)` as the single live selector over loaded collection-bundle rows and routed `_load_surface(...)` plus the grouped-replacement owner-path assertions through it.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^GROUPED_REPLACEMENT_COLLECTION_CASE_IDS = ' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - the task-local live-bundle probe from the acceptance block (`ok`)
