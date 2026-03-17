# RBR-0566: Publish the quantified-alternation broader-range bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the existing broader-range `{1,3}` quantified-alternation correctness publication with the exact bytes pair on the existing quantified-alternation correctness/parity path, so the frontier reopens on the tracked correctness surface before Rust-backed bytes parity lands.

## Deliverables
- `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py` remains the only correctness manifest for this slice and grows only by the 16 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(b|c){1,3}d"`
  - `rb"a(?P<word>b|c){1,3}d"`
- The added bytes cases stay pinned to the exact bounded observations for this published slice:
  - numbered compile metadata, module `search()` lower-bound hits on `b"zzabdzz"` and `b"zzacdzz"`, `Pattern.fullmatch()` success cases `b"abbbd"`, `b"abccd"`, and `b"abcbd"`, and bounded no-match texts `b"ad"` and `b"abbbcd"`;
  - named compile metadata, module `search()` lower-bound hits on `b"zzabdzz"` and `b"zzacdzz"`, `Pattern.fullmatch()` success cases `b"abbbd"`, `b"abccd"`, and `b"abcbd"`, and bounded no-match texts `b"ad"` and `b"abbbcd"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps the shared fixture-bundle contract honest after the manifest becomes mixed `str`/`bytes`, updates the broader-range quantified-alternation bundle expectations from `2` compile / `4` module / `10` pattern `str` cases to `4` / `8` / `20` with mixed text-model coverage, introduces `QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES` as the direct bytes follow-on anchor for this manifest, and routes the manifest's bytes rows through that anchor instead of silently widening the generic fixture-case buckets.
- The new direct bytes follow-on anchor in `tests/python/test_quantified_alternation_parity_suite.py` stays explicitly unsupported for `rebar` pending the later bytes parity follow-on, keeps the bounded success and miss texts above visible on the parity path, and does not fork a second bytes-only suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes pair behind `rebar._rebar`, the combined report should move from `1168` total / `1168` passed / `0` `unimplemented` across `111` manifests to `1184` / `1168` / `16`, and `match.quantified_alternation_broader_range` should publish `32` total / `16` passed / `16` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py --report .rebar/tmp/rbr-0566-quantified-alternation-broader-range-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes runtime behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, open-ended bytes follow-ons, nested-branch bytes work, conditional bytes work, backtracking-heavy bytes work, or another manifest family in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_quantified_alternation_parity_suite.py` surface.

## Notes
- Build on `RBR-0227`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py` currently contains `16` case ids and `0` bytes rows;
  - `tests/python/test_quantified_alternation_parity_suite.py` currently treats `quantified-alternation-broader-range-workflows` as `str`-only and carries no broader-range bytes follow-on anchor surface;
  - `reports/correctness/latest.py` currently publishes `match.quantified_alternation_broader_range` at `16` total / `16` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1168` total / `1168` passed / `0` `unimplemented`;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent broader-range `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing quantified-alternation parity surface before the benchmark surface mirrors the six adjacent broader-range `str` rows already published on `benchmarks/workloads/quantified_alternation_boundary.py`.
- 2026-03-17: Added the 16 bounded bytes counterparts to `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`, updated `tests/python/test_quantified_alternation_parity_suite.py` so the manifest is explicitly mixed `str`/`bytes` while the generic shared buckets stay on the shared `str` rows and the bytes rows route through `QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES` with explicit `rebar` skip gating, expanded `tests/conformance/correctness_expectations.py`, and republished `reports/correctness/latest.py`. The tracked combined scorecard now reads `1184` total / `1168` passed / `16` unimplemented across `111` manifests, and `match.quantified_alternation_broader_range` now reads `32` total / `16` passed / `16` unimplemented with `['bytes', 'str']` text-model coverage. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py --report .rebar/tmp/rbr-0566-quantified-alternation-broader-range-bytes.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
