# RBR-0584: Publish the quantified-alternation backtracking-heavy bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing bounded `{1,2}` quantified-alternation backtracking-heavy correctness publication with the exact bytes pair on the existing quantified-alternation correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py` remains the only correctness manifest for this slice and grows only by the twelve byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(b|bc){1,2}d"`
  - `rb"a(?P<word>b|bc){1,2}d"`
- The added bytes cases stay pinned to the exact bounded backtracking-heavy observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound `b`-branch hit on `b"zzabdzz"`, compiled `Pattern.fullmatch()` lower-bound `bc`-branch success on `b"abcd"`, compiled `Pattern.fullmatch()` second-repetition successes on `b"abbcd"`, `b"abcbd"`, and `b"abcbcd"`, plus the compiled `Pattern.fullmatch()` no-match on `b"abccd"`;
  - named compile metadata, module `search()` lower-bound `bc`-branch hit on `b"zzabcdzz"`, compiled `Pattern.fullmatch()` second-repetition successes on `b"abbd"` and `b"abcbd"`, plus the compiled `Pattern.fullmatch()` no-match on `b"abccd"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the backtracking-heavy bundle expectations from `2` compile / `2` module / `8` pattern `str` cases to `4` / `4` / `16` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this backtracking-heavy manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new backtracking-heavy bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the success and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1200` total / `1200` passed / `0` `unimplemented` across `111` manifests to `1212` / `1200` / `12`, and `match.quantified_alternation_backtracking_heavy` should publish `24` total / `12` passed / `12` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0584-quantified-alternation-backtracking-heavy-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, bounded quantified-alternation bytes work, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, nested-branch benchmark catch-up, conditional bytes work, branch-local-backreference bytes work, or another manifest family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_quantified_alternation_parity_suite.py` surface.

## Notes
- Queue this directly behind `RBR-0582` so the nested-branch bytes slice finishes its benchmark catch-up before overlapping-branch bytes publication reopens correctness work on the same quantified-alternation surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py` currently contains `12` case ids and `0` bytes rows;
  - `tests/python/test_quantified_alternation_parity_suite.py` currently treats `quantified-alternation-backtracking-heavy-workflows` as `str`-only, exposes no backtracking-heavy bytes follow-on anchor, and reserves `DIRECT_BYTES_FOLLOW_ON_SPECS` for the bounded, broader-range, open-ended, and nested-branch quantified-alternation manifests only;
  - `reports/correctness/latest.py` currently publishes `match.quantified_alternation_backtracking_heavy` at `12` total / `12` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1200` total / `1200` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent backtracking-heavy `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing quantified-alternation parity surface before the benchmark surface mirrors the six adjacent backtracking-heavy `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.
- 2026-03-18 completed: added the twelve bytes publication rows to `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`, routed them through one explicit unsupported bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py`, and refreshed `tests/conformance/correctness_expectations.py` plus the tracked published report. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0584-quantified-alternation-backtracking-heavy-bytes.py` (`24` total / `12` passed / `12` unimplemented), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, which now publishes `1212` total / `1200` passed / `12` unimplemented overall and `match.quantified_alternation_backtracking_heavy` at `24` / `12` / `12` with mixed `str`/`bytes` coverage.
