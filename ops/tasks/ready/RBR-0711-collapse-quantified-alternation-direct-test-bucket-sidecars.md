# RBR-0711: Collapse quantified-alternation direct-test bucket sidecars onto canonical follow-on specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the six hard-coded bytes follow-on entries from `QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS` in `tests/python/test_quantified_alternation_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` becomes the sole canonical owner of quantified-alternation bytes-follow-on bucket ordering and bundle-to-bucket routing.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` stops hard-coding these six bytes-follow-on bucket entries inside `QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS`:
  - `"bounded-bytes-follow-on": frozenset(...)`
  - `"broader-range-bytes-follow-on": frozenset(...)`
  - `"conditional-bytes-follow-on": frozenset(...)`
  - `"open-ended-bytes-follow-on": frozenset(...)`
  - `"nested-branch-bytes-follow-on": frozenset(...)`
  - `"backtracking-heavy-bytes-follow-on": frozenset(...)`
- The bytes-follow-on half of `QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS` derives directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of from the individual `QUANTIFIED_ALTERNATION_*_BUNDLE` constants:
  - keep the existing shared `"shared-compile"`, `"shared-module-search"`, and `"shared-pattern-fullmatch"` buckets intact; and
  - if a tiny file-local helper or inline comprehension is useful, keep it canonical-spec-driven instead of introducing another detached tuple/list/map block.
- Preserve the current effective ordering and routing exactly:
  - the direct-test bucket keys ending with `-bytes-follow-on` stay exactly `bounded-bytes-follow-on`, `broader-range-bytes-follow-on`, `conditional-bytes-follow-on`, `open-ended-bytes-follow-on`, `nested-branch-bytes-follow-on`, `backtracking-heavy-bytes-follow-on` in that order;
  - `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` keeps the same six ids in the same order: `bounded`, `broader-range`, `conditional`, `open-ended`, `nested-branch`, `backtracking-heavy`; and
  - for each follow-on spec, the routed direct-test bucket still equals the `frozenset` of `case.case_id` values from `spec.bundle.cases` where `case.text_model == "bytes"`.
- Keep canonical ownership unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, bundle pairing, supplemental case payloads, expected operation-helper counts, expected search/fullmatch text maps, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not change `FIXTURE_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `MATCH_GROUP_ACCESS_CASES`, or the direct parity surface they represent; and
  - do not broaden into removing the individual `QUANTIFIED_ALTERNATION_*_BUNDLE` constants elsewhere in the file during this task.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_quantified_alternation_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    '"bounded-bytes-follow-on": frozenset(',
    '"broader-range-bytes-follow-on": frozenset(',
    '"conditional-bytes-follow-on": frozenset(',
    '"open-ended-bytes-follow-on": frozenset(',
    '"nested-branch-bytes-follow-on": frozenset(',
    '"backtracking-heavy-bytes-follow-on": frozenset(',
):
    assert needle not in source, needle
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_quantified_alternation_parity_suite as mod

assert tuple(
    key
    for key in mod.QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS
    if key.endswith("-bytes-follow-on")
) == (
    "bounded-bytes-follow-on",
    "broader-range-bytes-follow-on",
    "conditional-bytes-follow-on",
    "open-ended-bytes-follow-on",
    "nested-branch-bytes-follow-on",
    "backtracking-heavy-bytes-follow-on",
)
assert tuple(
    frozenset(case.case_id for case in spec.bundle.cases if case.text_model == "bytes")
    for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
) == tuple(
    mod.QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS[f"{spec.id}-bytes-follow-on"]
    for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
)
print("ok")
PY`
  - `bash -lc "! rg -n '\"(bounded|broader-range|conditional|open-ended|nested-branch|backtracking-heavy)-bytes-follow-on\": frozenset\\(' tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored bucket-owner layer inside the quantified-alternation parity owner, not to reinterpret which bytes cases stay explicit, change direct-follow-on behavior, or broaden the suite beyond the current published slice.
- Prefer deriving the bytes-follow-on buckets directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over another detached bucket-label table or another helper registry.

## Notes
- `RBR-0711` is the correct frontier id for this queue even though old historical numeric holes still exist:
  - the live task tail is `RBR-0710`;
  - `rg -n "RBR-0711" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in the current checkout; and
  - the latest id scan found no reserved missing tail ids in `ops/state/backlog.md` or `ops/state/current_status.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The hard-coded direct-test bucket layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` currently passes (`777 passed in 1.06s`);
  - `rg -n "QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS|DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES|bounded-bytes-follow-on|broader-range-bytes-follow-on|conditional-bytes-follow-on|open-ended-bytes-follow-on|nested-branch-bytes-follow-on|backtracking-heavy-bytes-follow-on" tests/python/test_quantified_alternation_parity_suite.py` shows the six hard-coded bucket entries are declared only inside `QUANTIFIED_ALTERNATION_DIRECT_TEST_CASE_ID_BUCKETS`, while the direct-follow-on tests already parametrize from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`;
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: "bounded-bytes-follow-on": frozenset(`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all six hard-coded bucket entries still exist; and
  - the import probe in Acceptance already passes in the current checkout, so it pins the existing key order and bucket-to-spec mapping rather than future behavior.
- This simplification matches the current parity-harness information flow:
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` and `tests/python/test_open_ended_quantified_group_parity_suite.py` already derive their direct-test bytes-follow-on buckets from canonical spec records instead of hard-coding each follow-on bucket separately; and
  - `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` in the quantified-alternation owner already carries the canonical six-id ordering plus the bundle/case pairing needed to build those buckets without a second owner layer.
