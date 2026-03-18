# RBR-0643: Publish the nested broader-range open-ended branch-local-backreference replacement-template bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference replacement-template correctness publication with the exact bytes pair on the shared replacement surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes replacement parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){2,})\\2d"` with `rb"\\1x"` or `rb"\\2x"`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"` with `rb"\\g<outer>x"` or `rb"\\g<inner>x"`.
- The added bytes cases stay pinned to the exact broader-range open-ended replacement-template observations already published for the `str` slice:
  - numbered `module.sub(..., rb"\\1x", b"abbbd")`, numbered `module.subn(..., rb"\\2x", b"abbbdabcbccd", 1)`, numbered compiled `Pattern.sub(rb"\\1x", b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(rb"\\2x", b"zzacccdabbbdzz", 1)`;
  - named `module.sub(..., rb"\\g<outer>x", b"abcbccd")`, named `module.subn(..., rb"\\g<inner>x", b"abbbdacccd", 1)`, named compiled `Pattern.sub(rb"\\g<outer>x", b"zzacccdzz")`, and named compiled `Pattern.subn(rb"\\g<inner>x", b"zzacccdabcbccdzz", 1)`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps the shared replacement bundle contract honest after this manifest becomes mixed `str`/`bytes`, updates this manifest from 8 `str` replacement rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit on the shared suite:
  - if the live `rebar` result still reports placeholder behavior for those bytes rows, keep them visible through the existing shared replacement owner instead of forcing them through the current `str`-only compile-pattern and supplemental replacement partitions; and
  - if the live `rebar` result already matches CPython for those bytes rows, keep the mixed-text manifest landed without adding a bytes-only replacement suite or another manifest-specific parity module.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1302` total / `1302` passed / `0` `unimplemented` across `110` manifests to `1310` total cases across the same `110` manifests;
  - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows` moves from `8` total / `8` passed / `0` `unimplemented` with `['str']` text models to `16` total with mixed `str`/`bytes` coverage; and
  - the new bytes cases are reported honestly as either `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the published scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0643-nested-broader-range-open-ended-branch-local-backreference-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, the adjacent conditional or callable replacement flows, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_fixture_backed_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path.

## Notes
- `RBR-0643` is the next available feature task id in the current checkout; `RBR-0642` is already occupied by the done architecture cleanup task.
- Queue this directly behind `RBR-0641` so the broader `{2,}` callable benchmark catch-up closes before the adjacent non-conditional replacement-template bytes publication reopens correctness work on the shared replacement surface.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0643'` returned no matches before this file was added;
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` currently contains 8 `str` cases and 0 bytes rows;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently treats `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows` as `str`-only with 8 selected `str` case ids and `expected_text_models=frozenset({"str"})`, while the adjacent conditional replacement manifest on the same owner already uses mixed-text helper counts and `MIXED_TEXT_MODELS`;
  - `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` currently publish this manifest at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1302` total / `1302` passed / `0` `unimplemented` across `110` manifests;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str`, `module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str`, `pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str`, and `pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str`, and none of the planned `-bytes` mirrors, while the adjacent conditional bytes rows are already present on that same manifest; and
  - `tests/benchmarks/benchmark_expectations.py` already treats `nested-group-replacement-boundary` plus `broader-range-open-ended-branch-local-backreference` as the shared zero-gap slice for those four `str` rows, so a later Python-path benchmark catch-up can mirror the bytes pair without another synthesis pass.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared replacement surface before the benchmark surface mirrors the four adjacent `str` rows already published on `benchmarks/workloads/nested_group_replacement_boundary.py`.
- 2026-03-18 feature-implementation: added the eight bytes mirrors on the existing non-conditional replacement-template fixture, widened the shared replacement owner bundle to mixed `str`/`bytes`, and marked this manifest as a pending-bytes selected-frontier follow-on so the shared suite publishes the rows honestly without pretending direct Rust-backed parity exists yet. Updated `tests/conformance/correctness_expectations.py` and regenerated `reports/correctness/latest.py`; the tracked publication now reads `1310` total / `1302` passed / `8` `unimplemented` overall, while `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` now reads `16` total / `8` passed / `8` `unimplemented` with mixed `['bytes', 'str']` coverage and all eight new bytes rows published as `unimplemented`. Verified with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0643-nested-broader-range-open-ended-branch-local-backreference-replacement-bytes.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`.
