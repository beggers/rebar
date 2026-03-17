# RBR-0509: Publish the broader-range wider-ranged-repeat grouped-conditional bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing broader `{1,4}` grouped-alternation-plus-conditional correctness publication with the exact bytes pair already anchored in the wider-ranged-repeat parity suite, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|de){1,4})?(?(1)d|e)"`
  - `rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"`
- The added bytes cases stay pinned to the exact observations already carried by `BROADER_RANGE_CONDITIONAL_BYTES_CASES` in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`:
  - numbered compile metadata, module `search()` absent `b"zzaezz"`, module `search()` lower-bound `bc` `b"zzabcdzz"`, module `search()` lower-bound `de` `b"zzadedzz"`, `Pattern.fullmatch()` third-repetition mixed `b"abcbcded"`, `Pattern.fullmatch()` no-match missing-trailing-`d` `b"abcdede"`, and `Pattern.fullmatch()` no-match short `b"ad"`;
  - named compile metadata, module `search()` absent `b"zzaezz"`, module `search()` lower-bound `de` `b"zzadedzz"`, module `search()` upper-bound mixed `b"zzabcdedededzz"`, `Pattern.fullmatch()` third-repetition mixed `b"abcbcded"`, `Pattern.fullmatch()` no-match short `b"ad"`, and `Pattern.fullmatch()` no-match overflow `b"abcbcbcbcbcd"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes` and preserves `BROADER_RANGE_CONDITIONAL_BYTES_CASES` as the direct parity follow-on anchor instead of silently dropping or duplicating the bytes surface.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `983` total / `983` passed / `0` `unimplemented` across `111` manifests to `997` / `983` / `14`, and `match.broader_range_wider_ranged_repeat_quantified_group_alternation_conditional` should publish `28` total / `14` passed / `14` `unimplemented`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0509-broader-range-conditional-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes backtracking traces, benchmark rows, open-ended repeats, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0508`.
- 2026-03-17 feature-planning probes confirm this task is not stale: direct `rebar.compile(...)` checks against both bytes patterns still raise `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- The intended post-publication follow-on is `RBR-0510`, which should convert the same bytes pair behind `rebar._rebar` on the existing wider-ranged-repeat parity suite before benchmark catch-up or broader bytes follow-ons reopen the family.
