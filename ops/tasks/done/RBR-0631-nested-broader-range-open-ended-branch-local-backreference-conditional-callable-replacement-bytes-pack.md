# RBR-0631: Publish the nested broader-range open-ended branch-local-backreference conditional callable-replacement bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement correctness publication with the exact bytes pair on the shared callable parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` through `callable_match_group` on groups `1` or `2`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The added bytes cases stay pinned to the exact broader-range open-ended conditional callable-replacement observations already published for the `str` slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix="x"), b"abbbd")`, numbered `module.subn(..., callable_match_group(group=2, prefix="<", suffix=">"), b"abbbdabcbccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(..., b"zzacccdabbbdzz", 1)`;
  - named `module.sub(..., callable_match_group(group="outer", suffix="x"), b"abcbccd")`, named `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), b"abbbdacccd", 1)`, named compiled `Pattern.sub(..., b"zzacccdzz")`, and named compiled `Pattern.subn(..., b"zzacccdabcbccdzz", 1)`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the shared callable-replacement owner honest after this manifest becomes mixed `str`/`bytes`, updates `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` from 8 `str` rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit as the pending follow-on instead of forcing them through the current `str`-only compile, no-match, near-miss, or return-type-error partitions or another bytes-only callable suite.
- `tests/conformance/correctness_expectations.py` and `reports/correctness/latest.py` are regenerated honestly. With the live checkout still lacking this bytes callable pair behind `rebar._rebar`, the combined report should move from `1286` total / `1286` passed / `0` `unimplemented` across `111` manifests to `1294` / `1286` / `8`, and `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` should publish `16` total / `8` passed / `8` `unimplemented` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0631-nested-broader-range-open-ended-branch-local-backreference-conditional-callable-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, replacement-template flows, broader callback semantics, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_callable_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path.

## Notes
- Queue this directly behind `RBR-0629` so the broader `{2,}` conditional replacement-template bytes benchmark catch-up closes before adjacent callable-replacement bytes publication reopens correctness work on the same shared nested-group replacement frontier.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py` currently contains `8` `str` cases and `0` bytes rows;
  - `tests/python/test_callable_replacement_parity_suite.py` currently treats that manifest as `str`-only with `len(bundle.cases) == 8`, `text_models == {'str'}`, and helper counts of `2` each for `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`;
  - `reports/correctness/latest.py` currently publishes `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional.callable` at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1286` total / `1286` passed / `0` `unimplemented` across `111` manifests; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice as `module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str`, `module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str`, `pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str`, and `pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared callable parity surface before the benchmark surface mirrors the four adjacent `str` rows already published on `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.

## Completion Note
- 2026-03-18: Added the eight bytes callable-replacement publication rows to `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`, updated `tests/python/test_callable_replacement_parity_suite.py` so the manifest now publishes `16` mixed `str`/`bytes` rows while keeping the new bytes rows out of the shared str-only compile/no-match/near-miss/return-type-error partitions, expanded the representative scorecard expectations in `tests/conformance/correctness_expectations.py`, and republished `reports/correctness/latest.py`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`1366 passed, 1515 subtests passed in 27.33s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0631-nested-broader-range-open-ended-branch-local-backreference-conditional-callable-replacement-bytes.py` (`16` total / `8` passed / `8` unimplemented), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1294` total / `1286` passed / `8` unimplemented overall; target manifest `16` total / `8` passed / `8` unimplemented with `['bytes', 'str']` text models).
