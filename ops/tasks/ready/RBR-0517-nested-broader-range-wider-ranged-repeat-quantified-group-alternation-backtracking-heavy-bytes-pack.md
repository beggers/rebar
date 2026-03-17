# RBR-0517: Publish the nested broader-range wider-ranged-repeat grouped backtracking-heavy bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing nested broader `{1,4}` grouped backtracking-heavy correctness publication with the exact bytes pair on the existing wider-ranged-repeat correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(((bc|b)c){1,4})d"`
  - `rb"a(?P<outer>((bc|b)c){1,4})d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound `b"zzabcdzz"` and `b"zzabccdzz"`, `Pattern.fullmatch()` `b"abcbccd"`, `b"abccbcd"`, `b"abcbccbccbcd"`, and `b"abccbd"`;
  - named compile metadata, module `search()` `b"zzabccdzz"`, `b"zzabcbccdzz"`, and `b"zzabcbccbccbcdzz"`, and `Pattern.fullmatch()` `b"abccbcd"`, `b"abccbd"`, and `b"abcbcbcbcbcd"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader backtracking-heavy bundle expectations from `2` compile / `5` module / `7` pattern `str` cases to `4` / `10` / `14` with mixed text-model coverage, and introduces one direct bytes follow-on anchor on the existing parity path instead of silently dropping or duplicating the bytes surface.
- The new direct bytes follow-on anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0518`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this nested bytes pair behind `rebar._rebar`, the combined report should move from `1011` total / `1011` passed / `0` `unimplemented` across `111` manifests to `1025` / `1011` / `14`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0517-nested-broader-range-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into broader bytes grouped follow-ons already closed, benchmark rows, open-ended repeats, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0515`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py` currently contains only the 14 `str` cases for this nested broader `{1,4}` grouped backtracking-heavy slice and no `bytes` mirrors;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently expects the nested broader backtracking-heavy bundle to stay `str`-only at `2` compile / `5` module / `7` pattern cases and does not yet carry a direct bytes follow-on anchor for this manifest; and
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` at `14` total / `14` passed / `0` `unimplemented` with `['str']` coverage, while direct `PYTHONPATH=python ./.venv/bin/python` public-API probes still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The intended post-publication follow-on is `RBR-0518`, which should convert the same bytes pair behind `rebar._rebar` on the existing wider-ranged-repeat parity suite before benchmark catch-up revisits that family.
