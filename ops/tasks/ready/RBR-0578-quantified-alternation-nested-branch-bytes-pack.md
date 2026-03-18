# RBR-0578: Publish the quantified-alternation nested-branch bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing bounded `{1,2}` quantified-alternation nested-branch correctness publication with the exact bytes pair on the existing quantified-alternation correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py` remains the only correctness manifest for this slice and grows only by the ten byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c)|de){1,2}d"`
  - `rb"a(?P<word>(b|c)|de){1,2}d"`
- The added bytes cases stay pinned to the exact bounded nested-branch observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound inner-branch hit on `b"zzabdzz"`, compiled `Pattern.fullmatch()` lower-bound literal-branch success on `b"aded"`, compiled `Pattern.fullmatch()` second-repetition mixed-branches success on `b"abded"`, and compiled `Pattern.fullmatch()` no-match on `b"abde"`;
  - named compile metadata, module `search()` lower-bound literal-branch hit on `b"zzadedzz"`, compiled `Pattern.fullmatch()` lower-bound inner-branch success on `b"acd"`, compiled `Pattern.fullmatch()` second-repetition mixed-branches success on `b"adebd"`, and compiled `Pattern.fullmatch()` no-match on `b"adeb"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the nested-branch bundle expectations from `2` compile / `2` module / `6` pattern `str` cases to `4` / `4` / `12` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this nested-branch manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new nested-branch bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the success and no-match texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1190` total / `1190` passed / `0` `unimplemented` across `111` manifests to `1200` / `1190` / `10`, and `match.quantified_alternation_nested_branch` should publish `20` total / `10` passed / `10` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py --report .rebar/tmp/rbr-0578-quantified-alternation-nested-branch-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, bounded quantified-alternation bytes work, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, conditional bytes work, branch-local-backreference bytes work, backtracking-heavy bytes work, or another manifest family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_quantified_alternation_parity_suite.py` surface.

## Notes
- Build on `RBR-0576`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py` currently contains `10` case ids and `0` bytes rows;
  - `tests/python/test_quantified_alternation_parity_suite.py` currently treats `quantified-alternation-nested-branch-workflows` as `str`-only, exposes no nested-branch bytes follow-on anchor, and reserves `DIRECT_BYTES_FOLLOW_ON_SPECS` for the bounded, broader-range, and open-ended quantified-alternation manifests only;
  - `reports/correctness/latest.py` currently publishes `match.quantified_alternation_nested_branch` at `10` total / `10` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1190` total / `1190` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent nested-branch `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing quantified-alternation parity surface before the benchmark surface mirrors the six adjacent nested-branch `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.
