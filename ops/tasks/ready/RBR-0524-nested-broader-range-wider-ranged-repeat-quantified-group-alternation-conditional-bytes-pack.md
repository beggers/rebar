# RBR-0524: Publish the nested broader-range wider-ranged-repeat grouped-conditional bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing nested broader `{1,4}` grouped-alternation-plus-conditional correctness publication with the exact bytes pair on the existing wider-ranged-repeat correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(((bc|de){1,4})d)?(?(1)e|f)"`
  - `rb"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` absent `b"zzafzz"`, module `search()` lower-bound `bc` `b"zzabcdezz"`, module `search()` lower-bound `de` `b"zzadedezz"`, `Pattern.fullmatch()` mixed `b"abcbcdede"`, `Pattern.fullmatch()` no-match missing-conditional-`e` `b"abcbcded"`, and `Pattern.fullmatch()` no-match short `b"ae"`;
  - named compile metadata, module `search()` absent `b"zzafzz"`, module `search()` lower-bound `de` `b"zzadedezz"`, module `search()` upper-bound all-`de` `b"zzadededededezz"`, `Pattern.fullmatch()` mixed `b"abcbcdede"`, `Pattern.fullmatch()` no-match short `b"ae"`, and `Pattern.fullmatch()` no-match overflow `b"abcbcbcbcbcde"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader grouped-conditional bundle expectations from `2` compile / `6` module / `6` pattern `str` cases to `4` / `12` / `12` with mixed text-model coverage, and introduces `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES` as the direct parity follow-on anchor instead of silently dropping or duplicating the bytes surface.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1039` total / `1039` passed / `0` `unimplemented` across `111` manifests to `1053` / `1039` / `14`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0524-nested-broader-range-conditional-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes backtracking traces, benchmark rows, open-ended repeats, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0523`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py` currently contains only the 14 `str` cases for this nested broader `{1,4}` grouped-conditional slice and no `bytes` mirrors;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently expects the nested broader grouped-conditional bundle to stay `str`-only at `2` compile / `6` module / `6` pattern cases and does not yet carry `NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES`; and
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` at `14` total / `14` passed / `0` `unimplemented` with `['str']` coverage.
- The intended post-publication follow-on is `RBR-0525`, which should convert the same bytes pair behind `rebar._rebar` on the existing wider-ranged-repeat parity suite before benchmark catch-up or broader bytes follow-ons reopen that family.
