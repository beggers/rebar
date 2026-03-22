# RBR-0926: Collapse branch-local backreference match-group-access mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining detached `MATCH_GROUP_ACCESS_CASE_IDS` mirror from `tests/python/test_branch_local_backreference_parity_suite.py` so the branch-local owner derives that same 14-row match-group-access slice directly from the live simple-backreference bundles plus the existing nested and quantified branch-local owner bundles.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` no longer defines `MATCH_GROUP_ACCESS_CASE_IDS`:
  - delete the detached tuple instead of replacing it with another top-level tuple/list/set/map of the same ids; and
  - if helpers remain, keep them as tiny file-local live selectors over `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES`, `FIXTURE_BUNDLES_BY_MANIFEST_ID`, or the already-bound owner bundle constants in this file rather than adding a shared support module, registry table, or cached mirror.
- Preserve the current branch-local match-group-access surface exactly while routing it through live owner data:
  - `MATCH_GROUP_ACCESS_CASES` still resolves, in order, to `named-backreference-module-search-str`, `named-backreference-pattern-search-str`, `numbered-backreference-module-search-str`, `numbered-backreference-pattern-search-str`, `numbered-backreference-segment-module-search-str`, `numbered-backreference-prefix-pattern-search-str`, `nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str`, `nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str`, `nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str`, `nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str`, `quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str`, `quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str`, `quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str`, then `quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str`;
  - `test_match_group_access_rows_remain_on_shared_backreference_fixture_paths()` still proves that same ordered 14-row surface and still proves those rows remain `str`-only; and
  - do not add, drop, or reorder any of those 14 rows while deleting the mirror.
- Keep the existing branch-local parity coverage anchored to the same selected cases:
  - the two `@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ...)` tests still cover the same rows with `check_regs=True`;
  - `MATCH_CONVENIENCE_CASE_IDS`, `WORKFLOW_CASES`, direct-bytes follow-on routing, and bounded-pattern helper cases stay behaviorally unchanged; and
  - do not widen into fixture manifest edits, benchmark/report outputs, or tracked project-state prose.
- Keep this cleanup structural only:
  - do not change `MATCH_CONVENIENCE_MANIFEST_IDS`, `MATCH_CONVENIENCE_CASE_IDS`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, `DIRECT_BYTES_*` cases/specs, or branch-local regex behavior; and
  - keep the change limited to `tests/python/test_branch_local_backreference_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `bash -lc "! rg -n '^(MATCH_GROUP_ACCESS_CASE_IDS)\\s*=' tests/python/test_branch_local_backreference_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_branch_local_backreference_parity_suite import (
    FIXTURE_BUNDLES_BY_MANIFEST_ID,
    MATCH_GROUP_ACCESS_CASES,
    WHOLE_MANIFEST_BACKREFERENCE_BUNDLES,
)

nested_bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "nested-group-alternation-branch-local-backreference-workflows"
]
quantified_bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "quantified-alternation-branch-local-backreference-workflows"
]

simple_ids = tuple(
    case.case_id
    for bundle in WHOLE_MANIFEST_BACKREFERENCE_BUNDLES
    for case in bundle.cases
    if case.operation != "compile"
)
nested_live_ids = tuple(
    case.case_id
    for case in nested_bundle.cases
    if case.text_model == "str"
    and case.operation != "compile"
    and "no-match" not in case.case_id
)
quantified_live_ids = tuple(
    case.case_id
    for case in quantified_bundle.cases
    if case.text_model == "str"
    and case.operation != "compile"
    and "no-match" not in case.case_id
    and (
        case.operation == "module_call"
        or ("second-repetition" in case.case_id and "c-branch" not in case.case_id)
    )
)
live_ids = simple_ids + nested_live_ids + quantified_live_ids
assert live_ids == tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES)
assert live_ids == (
    "named-backreference-module-search-str",
    "named-backreference-pattern-search-str",
    "numbered-backreference-module-search-str",
    "numbered-backreference-pattern-search-str",
    "numbered-backreference-segment-module-search-str",
    "numbered-backreference-prefix-pattern-search-str",
    "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
    "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
    "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
    "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
)
print("ok", len(live_ids))
PY`

## Constraints
- Keep the change limited to `tests/python/test_branch_local_backreference_parity_suite.py`. Do not edit fixture manifests, shared parity-support helpers, harness modules, reports, README copy, or tracked state files in this run.
- Preserve the current branch-local match-group-access frontier exactly. The point is to delete one more owner-local representation layer, not to reinterpret which rows get match-group accessor coverage.

## Notes
- `RBR-0926` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0926|RBR-0927|RBR-0928|RBR-0929|RBR-0930' ops/state/backlog.md ops/state/current_status.md || true` returned no reserved follow-on ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 10` currently ends at `RBR-0925-catch-up-pattern-split-keyword-error-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no tracked blocked task file in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - `rg -n '^(MATCH_GROUP_ACCESS_CASE_IDS)\\s*=' tests/python/test_branch_local_backreference_parity_suite.py` currently finds the remaining mirror at line `533`; and
  - the task-local live-selector probe in Acceptance currently passes (`ok 14`), proving the file's existing owner bundles already recover the same ordered match-group-access surface without the detached tuple.

## Completion
- 2026-03-22: Removed the detached `MATCH_GROUP_ACCESS_CASE_IDS` mirror from `tests/python/test_branch_local_backreference_parity_suite.py` and replaced it with tiny live selectors over the existing simple, nested branch-local, and quantified branch-local owner bundles. Preserved the same ordered 14-row `MATCH_GROUP_ACCESS_CASES` surface, kept the two `@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ...)` parity tests unchanged, and verified with the full task-specified pytest run, the no-mirror `rg` check, and the task-local live-selector probe (`ok 14`).
