# RBR-0377: Fold match-group-access parity into the existing family suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Delete the cross-cutting `tests/python/test_match_group_access_parity.py` wrapper by moving its valid and invalid match-group accessor assertions onto the family suites that already own those published fixtures, so grouped-capture and branch-local-backreference parity stay on one legible fixture-backed path instead of a third overlapping suite.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- Delete `tests/python/test_match_group_access_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` absorbs the accessor-specific coverage currently selected in `tests/python/test_match_group_access_parity.py` from these published fixture rows, while continuing to derive them from the suite's existing fixture-backed path instead of another bundle table:
  - `grouped-module-search-single-capture-str`
  - `grouped-pattern-search-single-capture-str`
  - `named-group-module-search-metadata-str`
  - `named-group-pattern-search-metadata-str`
  - `systematic-optional-group-numbered-module-search-absent-str`
  - `systematic-optional-group-numbered-pattern-fullmatch-absent-str`
  - `systematic-optional-group-named-module-search-absent-str`
  - `systematic-optional-group-named-pattern-fullmatch-absent-str`
  - `nested-group-module-search-str`
  - `nested-group-pattern-fullmatch-str`
  - `named-nested-group-module-search-str`
  - `named-nested-group-pattern-fullmatch-str`
- `tests/python/test_branch_local_backreference_parity_suite.py` absorbs the accessor-specific coverage currently selected in `tests/python/test_match_group_access_parity.py` from these published fixture rows, again without reviving a second cross-family fixture bundle inventory:
  - `nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str`
  - `nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str`
  - `nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str`
  - `nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str`
  - `quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str`
  - `quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str`
  - `quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str`
  - `quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str`
- For each absorbed row, the owning suite asserts parity for valid `group`, `span`, `start`, `end`, and `Match.__getitem__` references across every numbered capture plus every published group name, and also asserts exception type plus `.args` parity for invalid `-1`, one-past-the-highest numeric group, and a missing group name chosen not to collide with the pattern's `groupindex`.
- If generic helper extraction is needed, extend `tests/python/fixture_parity_support.py` with only generic accessor-reference or exception-comparison helpers; do not create another dedicated access-support module and do not copy the current helper block into both destination suites.
- The fold preserves the current compile metadata, workflow parity, convenience-API parity, and supplemental miss coverage already present in `tests/python/test_grouped_capture_parity_suite.py` and `tests/python/test_branch_local_backreference_parity_suite.py`; this task only deletes the duplicate wrapper and relocates its accessor assertions.
- After the fold, `rg --files tests/python | rg 'test_match_group_access_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, or tracked state files.
- Do not broaden the match-group-access surface into unrelated families; keep the grouped-capture rows on `tests/python/test_grouped_capture_parity_suite.py` and the branch-local rows on `tests/python/test_branch_local_backreference_parity_suite.py`.
- Prefer deleting the duplicate suite over adding another registry, generated case layer, or cross-family abstraction. Failure output should still surface the owning suite, manifest, and fixture case ids clearly in pytest.

## Notes
- `tests/python/test_match_group_access_parity.py` is a 327-line duplicate wrapper over six fixtures already owned by `tests/python/test_grouped_capture_parity_suite.py` and `tests/python/test_branch_local_backreference_parity_suite.py`; it redefines `FixtureBundle`, fixture selection, compile execution, and accessor-error helpers only to add assertions that belong with those family suites.
- Both tracked and live JSON counts are already zero in the current checkout, so this is the next-priority architecture cleanup: delete duplicate parity plumbing instead of seeding another feature task or another helper layer.
