# RBR-0625: Publish the nested broader-range open-ended branch-local-backreference conditional replacement-template bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional replacement-template correctness publication with the exact bytes pair on the shared replacement surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes replacement parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` with `rb"\\1x"` or `rb"\\2x"`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` with `rb"\\g<outer>x"` or `rb"\\g<inner>x"`.
- The added bytes cases stay pinned to the exact broader-range open-ended conditional replacement-template observations already published for the `str` slice:
  - numbered `module.sub(..., rb"\\1x", b"abbbd")`, numbered `module.subn(..., rb"\\2x", b"abbbdabcbccd", 1)`, numbered compiled `Pattern.sub(rb"\\1x", b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(rb"\\2x", b"zzacccdabbbdzz", 1)`;
  - named `module.sub(..., rb"\\g<outer>x", b"abcbccd")`, named `module.subn(..., rb"\\g<inner>x", b"abbbdacccd", 1)`, named compiled `Pattern.sub(rb"\\g<outer>x", b"zzacccdzz")`, and named compiled `Pattern.subn(rb"\\g<inner>x", b"zzacccdabcbccdzz", 1)`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps the shared replacement bundle contract honest after this manifest becomes mixed `str`/`bytes`, updates this manifest from 8 `str` replacement rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit as pending follow-ons instead of forcing them through the existing `str`-only compile-pattern and supplemental replacement partitions or another bytes-only parity module.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes replacement pair behind `rebar._rebar`, the combined report should move from `1278` total / `1278` passed / `0` `unimplemented` across `111` manifests to `1286` / `1278` / `8`, and `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows` should publish `16` total / `8` passed / `8` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py --report .rebar/tmp/rbr-0625-nested-broader-range-open-ended-branch-local-backreference-conditional-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, callable-replacement flows, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_fixture_backed_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path.

## Notes
- Queue this directly behind `RBR-0623` so the broader `{2,}` conditional branch-local bytes benchmark catch-up closes before adjacent replacement-template bytes publication reopens correctness work on the shared replacement surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py` currently contains 8 `str` cases and 0 bytes rows;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently treats `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows` as `str`-only with 4 module and 4 pattern cases, and the shared compile-pattern plus supplemental replacement partitions still assume `str`-only patterns for this surface;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish this manifest at `8` total / `8` passed / `0` `unimplemented`, while the combined report stays at `1278` total / `1278` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` already publishes the four adjacent `str` replacement-template benchmark rows for this exact slice as `module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str`, `module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str`, `pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str`, and `pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes replacement workflows at `rebar.sub(...)`.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared replacement surface before the benchmark surface mirrors the four adjacent `str` rows already published on `benchmarks/workloads/nested_group_replacement_boundary.py`.
