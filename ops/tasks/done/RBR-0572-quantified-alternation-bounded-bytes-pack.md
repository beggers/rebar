# RBR-0572: Publish the bounded quantified-alternation bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17
Completed: 2026-03-17

## Goal
- Extend the existing bounded `{1,2}` quantified-alternation correctness publication with the exact bytes pair on the existing quantified-alternation correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_workflows.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_workflows.py` remains the only correctness manifest for this slice and grows only by the six byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(b|c){1,2}d"`
  - `rb"a(?P<word>b|c){1,2}d"`
- The added bytes cases stay pinned to the exact bounded observations already published for the `str` slice:
  - numbered compile metadata, module `search()` lower-bound hit on `b"zzacdz"`, and compiled `Pattern.fullmatch()` second-repetition success on `b"abcd"`;
  - named compile metadata, module `search()` second-repetition hit on `b"zzacbdzz"`, and compiled `Pattern.fullmatch()` lower-bound success on `b"abd"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the bounded quantified-alternation bundle expectations from `2` compile / `2` module / `2` pattern `str` cases to `4` / `4` / `4` with mixed text-model coverage, introduces one direct bytes follow-on anchor for this bounded manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic shared buckets.
- The new bounded bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the bounded success texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1184` total / `1184` passed / `0` `unimplemented` across `111` manifests to `1190` / `1184` / `6`, and `match.quantified_alternation` should publish `12` total / `6` passed / `6` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_workflows.py --report .rebar/tmp/rbr-0572-quantified-alternation-bounded-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, broader-range bytes work, open-ended bytes work, nested-branch bytes work, conditional bytes work, backtracking-heavy bytes work, or another manifest family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_quantified_alternation_parity_suite.py` surface.

## Notes
- Build on `RBR-0570`.
- 2026-03-17 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/quantified_alternation_workflows.py` currently contains `6` case ids and `0` bytes rows;
  - `tests/python/test_quantified_alternation_parity_suite.py` currently treats `quantified-alternation-workflows` as `str`-only and routes only the broader-range and open-ended manifests through direct bytes follow-on anchors;
  - `reports/correctness/latest.py` currently publishes `match.quantified_alternation` at `6` total / `6` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1184` total / `1184` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent bounded `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing quantified-alternation parity surface before the benchmark surface mirrors the six adjacent bounded `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.

## Completion
- Added the six bounded bytes rows to `tests/conformance/fixtures/quantified_alternation_workflows.py` and routed them through one explicit bounded bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py`; that direct bytes anchor stays `rebar`-unsupported until the later parity task lands.
- Regenerated the tracked published correctness report in `reports/correctness/latest.py`; the combined scorecard now records `1190` total / `1184` passed / `6` unimplemented cases, and `match.quantified_alternation` now records `12` total / `6` passed / `6` unimplemented with mixed `bytes`/`str` coverage.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_workflows.py --report .rebar/tmp/rbr-0572-quantified-alternation-bounded-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
