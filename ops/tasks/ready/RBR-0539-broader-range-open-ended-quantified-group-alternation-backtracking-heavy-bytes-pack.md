# RBR-0539: Publish the broader-range open-ended grouped backtracking-heavy bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing broader-range open-ended `{2,}` grouped backtracking-heavy correctness publication with the exact bytes pair on the existing open-ended correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|b)c){2,}d"`
  - `rb"a(?P<word>(bc|b)c){2,}d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound short-branch `b"zzabcbcdzz"`, module `search()` lower-bound long-branch `b"zzabcbccdzz"`, `Pattern.fullmatch()` second-repetition long-then-short `b"abccbcd"`, `Pattern.fullmatch()` fourth-repetition short-only `b"abcbcbcbcd"`, `Pattern.fullmatch()` no-match one-repetition `b"abcd"`, and `Pattern.fullmatch()` no-match invalid-tail `b"abccbd"`;
  - named compile metadata, module `search()` lower-bound long-branch `b"zzabcbccdzz"`, module `search()` second-repetition long-then-short `b"zzabccbcdzz"`, module `search()` fourth-repetition short-only `b"zzabcbcbcbcdzz"`, module `search()` no-match invalid-tail `b"zzabccbdzz"`, `Pattern.fullmatch()` second-repetition short-then-long `b"abcbccd"`, and `Pattern.fullmatch()` no-match one-repetition `b"abcd"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the broader-range grouped backtracking-heavy bundle expectations from `2` compile / `6` module / `6` pattern `str` cases to `4` / `12` / `12` with mixed text-model coverage, and introduces `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` as the direct bytes follow-on anchor while routing this manifest's bytes rows away from the generic case buckets.
- The new direct bytes follow-on anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0540`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1094` total / `1094` passed / `0` `unimplemented` across `111` manifests to `1108` / `1094` / `14`, and `match.broader_range_open_ended_quantified_group_alternation_backtracking_heavy` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0539-broader-range-open-ended-grouped-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, broader-range open-ended grouped-conditional follow-ons already closed, nested grouped follow-ons, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_open_ended_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0538`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` currently contains only the 14 `str` cases for this broader-range open-ended `{2,}` grouped backtracking-heavy slice and no `bytes` mirrors;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently expects the broader-range grouped backtracking-heavy bundle to stay `str`-only at `2` compile / `6` module / `6` pattern cases and does not yet carry a direct bytes follow-on anchor or direct-follow-on routing for this manifest;
  - `reports/correctness/latest.py` currently publishes `match.broader_range_open_ended_quantified_group_alternation_backtracking_heavy` at `14` total / `14` passed / `0` `unimplemented` with `['str']` coverage, while the combined report stays at `1094` total / `1094` passed / `0` `unimplemented` across `111` manifests; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0540`, which should convert the same bytes pair behind `rebar._rebar` on the existing open-ended parity surface before benchmark catch-up widens that broader-range family.
