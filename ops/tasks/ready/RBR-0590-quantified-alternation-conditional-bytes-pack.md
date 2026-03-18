# RBR-0590: Publish the quantified-alternation conditional bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing bounded `{1,2}` quantified-alternation-plus-conditional correctness publication with the exact bytes pair on the existing quantified-alternation correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_conditional_workflows.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_conditional_workflows.py` remains the only correctness manifest for this slice and grows only by the twelve byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){1,2})?(?(1)d|e)"`
  - `rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)"`
- The added bytes cases stay pinned to the exact bounded conditional observations already published for the `str` slice:
  - numbered compile metadata, module `search()` absent-arm success on `b"zzaezz"`, module `search()` lower-bound `b`-branch success on `b"zzabdzz"`, compiled `Pattern.fullmatch()` second-repetition `b`-branch success on `b"abbd"`, compiled `Pattern.fullmatch()` second-repetition mixed-branch success on `b"abcd"`, and compiled `Pattern.fullmatch()` no-match on `b"abe"`;
  - named compile metadata, module `search()` absent-arm success on `b"zzaezz"`, module `search()` lower-bound `c`-branch success on `b"zzacdzz"`, compiled `Pattern.fullmatch()` second-repetition `c`-branch success on `b"accd"`, compiled `Pattern.fullmatch()` second-repetition mixed-branch success on `b"abcd"`, and compiled `Pattern.fullmatch()` no-match on `b"acce"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the quantified-alternation conditional bundle expectations from `2` compile / `4` module / `6` pattern `str` cases to `4` / `8` / `12` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this conditional manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new quantified-alternation conditional bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the absent-arm, present-arm, success, and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1212` total / `1212` passed / `0` `unimplemented` across `111` manifests to `1224` / `1212` / `12`, and `match.quantified_alternation_conditional` should publish `24` total / `12` passed / `12` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0590-quantified-alternation-conditional-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, generated parity-matrix expansion, another quantified-alternation manifest, or another manifest family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_quantified_alternation_parity_suite.py` surface.

## Notes
- Queue this directly behind `RBR-0588` so the backtracking-heavy bytes benchmark catch-up closes before quantified-alternation conditional bytes publication reopens correctness work on the same quantified-alternation family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/quantified_alternation_conditional_workflows.py` currently contains `12` case ids and `0` bytes rows;
  - `tests/python/test_quantified_alternation_parity_suite.py` currently treats `quantified-alternation-conditional-workflows` as `str`-only, exposes no conditional bytes follow-on anchor, and reserves `DIRECT_BYTES_FOLLOW_ON_SPECS` for the bounded, broader-range, open-ended, nested-branch, and backtracking-heavy quantified-alternation manifests only;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish `match.quantified_alternation_conditional` at `12` total / `12` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1212` total / `1212` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent conditional `str` benchmark rows for this exact numbered and named pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing quantified-alternation parity surface before the benchmark surface mirrors the six adjacent conditional `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.
