# RBR-0520: Publish the nested broader-range wider-ranged-repeat grouped-alternation bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing nested broader `{1,4}` grouped-alternation correctness publication with the exact bytes pair on the existing wider-ranged-repeat correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py` remains the only correctness manifest for this slice and grows only by the 14 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|de){1,4})d"`
  - `rb"a(?P<outer>(bc|de){1,4})d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`, `Pattern.fullmatch()` successes on `b"abcbcded"` and `b"adedededed"`, and bounded no-match texts `b"ae"` and `b"abcbcdede"`;
  - named compile metadata, module `search()` lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`, `Pattern.fullmatch()` successes on `b"abcbcded"` and `b"adedededed"`, and bounded no-match texts `b"ae"` and `b"abcbcbcbcbcd"`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested broader grouped-alternation bundle expectations from `2` compile / `4` module / `8` pattern `str` cases to `4` / `8` / `16` with mixed text-model coverage, and introduces one direct bytes follow-on anchor on the existing parity path instead of silently dropping or duplicating the bytes surface.
- The new direct bytes follow-on anchor in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0522`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this nested bytes pair behind `rebar._rebar`, the combined report should move from `1025` total / `1025` passed / `0` `unimplemented` across `111` manifests to `1039` / `1025` / `14`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` should publish `28` total / `14` passed / `14` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0520-nested-broader-range-grouped-alternation-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into nested broader grouped-conditional bytes follow-ons, benchmark rows, open-ended repeats, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` surface.

## Notes
- 2026-03-17 completion:
  - Added the 14 bytes mirrors to the existing nested broader `{1,4}` grouped-alternation manifest, keeping this slice on one shared correctness fixture.
  - Updated the wider-ranged-repeat parity suite bundle contract to mixed `str`/`bytes` coverage and added one direct nested bytes follow-on anchor that stays explicitly unsupported for `rebar` pending `RBR-0522`.
  - Regenerated the tracked combined scorecard in `reports/correctness/latest.py`; the published report now shows `1039` total / `1025` passed / `14` unimplemented across `111` manifests, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` now shows `28` total / `14` passed / `14` unimplemented with `['bytes', 'str']` coverage.
  - Verified with:
    - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
    - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0520-nested-broader-range-grouped-alternation-bytes.py`
    - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Build on `RBR-0519`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py` currently contains only the 14 `str` cases for this nested broader `{1,4}` grouped-alternation slice and no `bytes` mirrors;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently expects the nested broader grouped-alternation bundle to stay `str`-only at `2` compile / `4` module / `8` pattern cases and does not yet carry a direct bytes follow-on anchor for this manifest;
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation` at `14` total / `14` passed / `0` `unimplemented` with `['str']` coverage; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0522`, which should convert the same bytes pair behind `rebar._rebar` on the existing wider-ranged-repeat parity surface before benchmark catch-up or nested broader grouped-conditionals broaden that family.
