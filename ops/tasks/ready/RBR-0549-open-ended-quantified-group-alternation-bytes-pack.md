# RBR-0549: Publish the open-ended quantified-group alternation bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing open-ended `{1,}` grouped-alternation correctness publication with the exact bytes pair on the existing open-ended correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py` remains the only correctness manifest for this slice and grows only by the 16 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(bc|de){1,}d"`
  - `rb"a(?P<word>bc|de){1,}d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`, `Pattern.fullmatch()` success cases `b"abcbcd"`, `b"abcded"`, and `b"abcbcded"`, and bounded no-match texts `b"ad"` and `b"abed"`;
  - named compile metadata, module `search()` lower-bound hits on `b"zzabcdzz"` and `b"zzadedzz"`, `Pattern.fullmatch()` success cases `b"abcded"`, `b"abcbcded"`, and `b"adededed"`, and bounded no-match texts `b"ad"` and `b"abed"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the open-ended grouped-alternation bundle expectations from `2` compile / `4` module / `10` pattern `str` cases to `4` / `8` / `20` with mixed text-model coverage, introduces `OPEN_ENDED_ALTERNATION_BYTES_CASES` as the direct bytes follow-on anchor, and routes the manifest's bytes rows through that anchor instead of the generic case buckets.
- The new direct bytes follow-on anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0550`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1120` total / `1120` passed / `0` `unimplemented` across `111` manifests to `1136` / `1120` / `16`, and `match.open_ended_quantified_group_alternation` should publish `32` total / `16` passed / `16` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0549-open-ended-grouped-alternation-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, broader-range open-ended grouped work, grouped-conditionals, grouped backtracking-heavy rows, benchmark rows, or a second bytes-only fixture or parity suite.
- Keep the future parity follow-on anchored to the existing `tests/python/test_open_ended_quantified_group_parity_suite.py` surface.

## Notes
- Build on `RBR-0546`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py` currently contains only the 16 `str` cases for this open-ended `{1,}` grouped-alternation slice and no `bytes` mirrors;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently expects the open-ended grouped-alternation bundle to stay `str`-only at `2` compile / `4` module / `10` pattern cases and does not yet carry a direct bytes follow-on anchor for this manifest;
  - `reports/correctness/latest.py` currently publishes `match.open_ended_quantified_group_alternation` at `16` total / `16` passed / `0` `unimplemented` with `['str']` coverage, while the combined report stays at `1120` total / `1120` passed / `0` `unimplemented` across `111` manifests; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0550`, which should convert the same bytes pair behind `rebar._rebar` on the existing open-ended parity surface before benchmark catch-up mirrors the adjacent source-tree `str` rows onto the bytes path.
