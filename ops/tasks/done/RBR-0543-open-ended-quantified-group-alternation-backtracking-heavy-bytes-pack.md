# RBR-0543: Publish the open-ended grouped backtracking-heavy bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing open-ended `{1,}` grouped backtracking-heavy correctness publication with the exact bytes pair on the existing open-ended correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` remains the only correctness manifest for this slice and grows only by the 12 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((bc|b)c){1,}d"`
  - `rb"a(?P<word>(bc|b)c){1,}d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound short-branch `b"zzabcdzz"`, `Pattern.fullmatch()` lower-bound long-branch `b"abccd"`, `Pattern.fullmatch()` second-repetition short-then-short `b"abcbcd"`, `Pattern.fullmatch()` second-repetition short-then-long `b"abcbccd"`, and `Pattern.fullmatch()` no-match overlap-tail `b"abcccd"`;
  - named compile metadata, module `search()` lower-bound long-branch `b"zzabccdzz"`, module `search()` second-repetition long-then-short `b"zzabccbcdzz"`, module `search()` third-repetition mixed `b"zzabcbccbcdzz"`, `Pattern.fullmatch()` fourth-repetition short-only `b"abcbcbcbcd"`, and module `search()` no-match invalid-tail `b"zzabccbdzz"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the open-ended grouped backtracking-heavy bundle expectations from `2` compile / `5` module / `5` pattern `str` cases to `4` / `10` / `10` with mixed text-model coverage, introduces `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` as the direct bytes follow-on anchor, and keeps the manifest's compile / module / pattern accounting explicit and internally consistent.
- The new direct bytes follow-on anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` stays explicitly unsupported for `rebar` pending `RBR-0544`, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1108` total / `1108` passed / `0` `unimplemented` across `111` manifests to `1120` / `1108` / `12`, and `match.open_ended_quantified_group_alternation_backtracking_heavy` should publish `24` total / `12` passed / `12` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0543-open-ended-grouped-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, broader-range follow-ons already closed, or a second bytes-only fixture or parity suite.
- Keep the future parity and benchmark follow-ons anchored to the existing `tests/python/test_open_ended_quantified_group_parity_suite.py` and `benchmarks/workloads/open_ended_quantified_group_boundary.py` surfaces.

## Notes
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` currently contains only the 12 `str` cases for this open-ended `{1,}` grouped backtracking-heavy slice and no `bytes` mirrors;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently expects the open-ended grouped backtracking-heavy bundle to stay `str`-only at `2` compile / `5` module / `5` pattern cases and carries no `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES` anchor;
  - `reports/correctness/latest.py` currently publishes `match.open_ended_quantified_group_alternation_backtracking_heavy` at `12` total / `12` passed / `0` `unimplemented` with `['str']` coverage, while the combined report stays at `1108` total / `1108` passed / `0` `unimplemented` across `111` manifests;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`; and
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` already publishes the six adjacent measured `str` backtracking-heavy rows for this exact `{1,}` slice, so later benchmark catch-up should reuse that existing Python-path manifest instead of inventing another benchmark family.
- The surviving follow-on after this task is `RBR-0544`, which should convert the same bytes pair behind `rebar._rebar` on the existing open-ended parity surface before benchmark catch-up mirrors the existing source-tree backtracking-heavy rows onto the bytes path.
- Completed 2026-03-17:
  - Added the 12 bytes mirrors for `rb"a((bc|b)c){1,}d"` and `rb"a(?P<word>(bc|b)c){1,}d"` to the existing `open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` manifest without forking a second fixture.
  - Updated `tests/python/test_open_ended_quantified_group_parity_suite.py` so the mixed manifest now expects `4` compile / `10` module / `10` pattern rows, routes the new bytes cases through `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`, and skips the `rebar` backend there explicitly pending `RBR-0544`.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`1566 passed, 14 skipped, 1172 subtests passed`).
  - Verified the focused manifest report at `.rebar/tmp/rbr-0543-open-ended-grouped-backtracking-heavy-bytes.py`, which now publishes `24` total / `12` passed / `12` unimplemented for this manifest-local slice.
  - Regenerated the tracked `reports/correctness/latest.py`; the published combined scorecard now reports `1120` total / `1108` passed / `12` unimplemented across `111` manifests, and `match.open_ended_quantified_group_alternation_backtracking_heavy` now reports `24` total / `12` passed / `12` unimplemented with `['bytes', 'str']` coverage.
