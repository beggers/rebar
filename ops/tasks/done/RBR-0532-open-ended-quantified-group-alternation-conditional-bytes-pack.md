# RBR-0532: Publish the open-ended grouped-alternation-plus-conditional bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing open-ended `{1,}` grouped-alternation-plus-conditional correctness publication with the exact bytes pair on the existing open-ended correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py` remains the only correctness manifest for this slice and grows only by the 13 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|de){1,})?(?(1)d|e)"`
  - `rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` absent/lower-bound hits on `b"zzaezz"`, `b"zzabcdzz"`, and `b"zzadedzz"`, plus `Pattern.fullmatch()` success cases `b"abcded"` and `b"abcbcded"` and the bounded miss `b"abcde"`;
  - named compile metadata, module `search()` absent/lower-bound/fourth-repetition hits on `b"zzaezz"`, `b"zzadedzz"`, and `b"zzadedededzz"`, plus `Pattern.fullmatch()` success/miss cases `b"abcbcded"` and `b"ad"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the open-ended grouped-conditional bundle expectations from `2` compile / `6` module / `5` pattern `str` cases to `4` / `12` / `10` with mixed text-model coverage, and introduces `OPEN_ENDED_CONDITIONAL_BYTES_CASES` as the direct bytes follow-on anchor instead of silently dropping or duplicating the bytes surface.
- The new direct bytes follow-on anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0533`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1067` total / `1067` passed / `0` `unimplemented` across `111` manifests to `1080` / `1067` / `13`, and `match.open_ended_quantified_group_alternation_conditional` should publish `26` total / `13` passed / `13` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0532-open-ended-grouped-conditional-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, broader-range open-ended grouped work, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_open_ended_quantified_group_parity_suite.py` surface.

## Notes
- 2026-03-17 completion:
  - Added the 13 bytes mirrors to the existing open-ended `{1,}` grouped-alternation-plus-conditional manifest, keeping this slice on one shared correctness fixture.
  - Updated the open-ended parity suite bundle contract to mixed `str`/`bytes` coverage and added one direct grouped-conditional bytes follow-on anchor that stays explicitly unsupported for `rebar` pending `RBR-0533`.
  - Regenerated the tracked combined scorecard in `reports/correctness/latest.py`; the published report now shows `1080` total / `1067` passed / `13` unimplemented across `111` manifests, and `match.open_ended_quantified_group_alternation_conditional` now shows `26` total / `13` passed / `13` unimplemented with `['bytes', 'str']` coverage.
  - Verified with:
    - `cargo build -p rebar-cpython`
    - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
    - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0532-open-ended-grouped-conditional-bytes.py`
    - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Build on `RBR-0530`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py` currently contains only the 13 `str` cases for this open-ended `{1,}` grouped-conditional slice and no `bytes` mirrors;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently expects the open-ended grouped-conditional bundle to stay `str`-only at `2` compile / `6` module / `5` pattern cases and does not yet carry a direct bytes follow-on anchor for this manifest;
  - `reports/correctness/latest.py` currently publishes `match.open_ended_quantified_group_alternation_conditional` at `13` total / `13` passed / `0` `unimplemented` with `['str']` coverage, while the combined report stays at `1067` total / `1067` passed / `0` `unimplemented` across `111` manifests; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0533`, which should convert the same bytes pair behind `rebar._rebar` on the existing open-ended parity surface before benchmark catch-up widens that family.
