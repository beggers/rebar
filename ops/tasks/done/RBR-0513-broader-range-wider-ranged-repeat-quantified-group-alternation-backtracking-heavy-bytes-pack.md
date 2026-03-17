# RBR-0513: Publish the broader-range wider-ranged-repeat grouped backtracking-heavy bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing broader `{1,4}` grouped backtracking-heavy correctness publication with the exact bytes pair already anchored on the wider-ranged-repeat parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|b)c){1,4}d"`
  - `rb"a(?P<word>(bc|b)c){1,4}d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch `b"zzabcdzz"`, module `search()` lower-bound `bc`-branch `b"zzabccdzz"`, `Pattern.fullmatch()` second-repetition short-then-long `b"abcbccd"`, `Pattern.fullmatch()` second-repetition long-then-short `b"abccbcd"`, `Pattern.fullmatch()` fourth-repetition mixed `b"abcbccbccbcd"`, and `Pattern.fullmatch()` no-match invalid-tail `b"abccbd"`;
  - named compile metadata, module `search()` lower-bound `bc`-branch `b"zzabccdzz"`, module `search()` second-repetition short-then-long `b"zzabcbccdzz"`, module `search()` fourth-repetition mixed `b"zzabcbccbccbcdzz"`, `Pattern.fullmatch()` second-repetition long-then-short `b"abccbcd"`, `Pattern.fullmatch()` no-match invalid-tail `b"abccbd"`, and `Pattern.fullmatch()` no-match overflow `b"abcbcbcbcbcd"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the broader-range backtracking-heavy bundle expectations from `2` compile / `5` module / `7` pattern `str` cases to `4` / `10` / `14` with mixed text-model coverage, and introduces or refreshes one direct bytes follow-on anchor on the existing parity path instead of silently dropping or duplicating the bytes surface.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `997` total / `997` passed / `0` `unimplemented` across `111` manifests to `1011` / `997` / `14`, and `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0513-broader-range-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes grouped-conditionals already closed, nested broader bytes slices, benchmark rows, open-ended repeats, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0512`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py` currently contains only the 14 `str` cases for this broader `{1,4}` grouped backtracking-heavy slice and no `bytes` mirrors;
  - `reports/correctness/latest.py` currently publishes `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` at `14` total / `14` passed / `0` `unimplemented` with `text_models == ['str']`;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The intended post-publication follow-on is `RBR-0514`, which should convert the same bytes pair behind `rebar._rebar` on the existing wider-ranged-repeat parity suite before benchmark catch-up or broader bytes follow-ons reopen the family.
- 2026-03-17 feature-implementation completed this publication-only slice by adding the 14 `bytes` counterparts to `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`, updating `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so the bundle contract stays mixed `str`/`bytes` while the new `BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES` anchor skips `rebar` pending `RBR-0514`, extending `tests/conformance/correctness_expectations.py` to include the mirrored bytes cases, and regenerating `reports/correctness/latest.py` to `1011` total / `997` passed / `14` unimplemented overall with `match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy` at `28` total / `14` passed / `14` unimplemented.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0513-broader-range-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
