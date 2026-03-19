# RBR-0698: Publish the nested broader-range open-ended backtracking-heavy callable-replacement bytes pair

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the existing broader-range open-ended `{2,}` nested grouped backtracking-heavy callable-replacement correctness publication with the exact bytes pair on the shared callable parity surface, so the frontier reopens on the tracked correctness path before any Rust-backed bytes parity or later Python-path benchmark catch-up lands.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a(((bc|b)c){2,})d"` through `callable_match_group` on groups `1` or `3`;
  - `rb"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The added bytes cases stay pinned to the exact broader-range open-ended `{2,}` backtracking-heavy callable-replacement observations already published for the `str` slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abcbcd")`, numbered `module.subn(..., callable_match_group(group=3, prefix=b"<", suffix=b">"), b"abccbccdabcbcd", 1)`, numbered compiled `Pattern.sub(..., b"zzabccbcdzz")`, and numbered compiled `Pattern.subn(..., b"zzabcbcbcbcdabccbccdzz", 1)`;
  - named `module.sub(..., callable_match_group(group="outer", suffix=b"x"), b"abccbcd")`, named `module.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"abccbccdabcbcd", 1)`, named compiled `Pattern.sub(..., b"zzabcbcbcbcdzz")`, and named compiled `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzabcbcbcbcdabccbccdzz", 1)`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the shared callable-replacement owner honest after this manifest becomes mixed `str`/`bytes`, updates `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` from 8 `str` rows to 16 mixed rows with compile patterns growing from the two current `str` patterns to the four `str` plus `bytes` variants and helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit on the shared suite:
  - if the live `rebar` result still reports placeholder behavior for those bytes rows, represent them through `pending_rebar_case_ids` instead of forcing them through the current compile, no-match, near-miss, or return-type-error partitions; and
  - if the live `rebar` result already matches CPython for those bytes rows, keep the mixed-text manifest landed without adding a bytes-only callable suite or another manifest-specific parity module.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1374` total / `1374` passed / `0` `unimplemented` across `114` manifests to `1382` total across the same `114` manifests, with the new 8-case slice reported as either passing or `unimplemented` according to the live `rebar` result; and
  - `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` moves from `8` total / `8` passed / `0` `unimplemented` with `['str']` text models to `16` total with mixed `str`/`bytes` coverage.
- The new bytes cases are reported honestly as either `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the published scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0698-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, replacement-template flows, broader callback semantics, another grouped family, or deeper grouped execution in this run.
- Keep any later parity follow-on anchored to the existing `tests/python/test_callable_replacement_parity_suite.py` surface and any later benchmark follow-on on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path.

## Notes
- `RBR-0698` is the next available feature task id in the current checkout; `RBR-0697` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after the drained `RBR-0696` head so the broader-range open-ended `{2,}` nested grouped backtracking-heavy callable frontier reopens through one exact mixed-text correctness follow-on on the same shared owner surface instead of pausing for another synthesis pass.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0696-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-benchmark-catch-up.md` records that the adjacent `str` benchmark catch-up is complete on the shared `nested_group_callable_replacement_boundary.py` path, so the next bounded follow-on is the corresponding bytes correctness publication rather than another `str` benchmark expansion;
  - `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py` currently contains the 8 published `str` rows for this manifest and no bytes rows;
  - `tests/python/test_callable_replacement_parity_suite.py` currently treats `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` as `str`-only with the 8 published `str` case ids, two `str` compile patterns, `CALLABLE_STR_ONLY_OPERATION_HELPER_COUNTS`, and `expected_text_models == {'str'}`; and
  - `reports/correctness/latest.py` currently publishes `1374` total / `1374` passed / `0` `unimplemented` across `114` manifests, while `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` stays at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, so this mixed-text publication slice is not already represented on the tracked scorecard.
- 2026-03-19 completion:
  - Added the 8 bytes callable-replacement counterparts to the existing manifest, keeping this as the only correctness fixture for the `{2,}` nested broader-range open-ended backtracking-heavy callable slice.
  - Updated the shared callable parity suite to treat this manifest as mixed `str`/`bytes` with four compile patterns, mixed helper counts, and the 8 new bytes case ids recorded in `pending_rebar_case_ids` because live `rebar` still reports scaffold `NotImplementedError` outcomes for them.
  - Regenerated the tracked combined correctness report. The tracked `reports/correctness/latest.py` diff now publishes `1382` total / `1374` passed / `8` `unimplemented` across `114` manifests, and `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` now publishes `16` total / `8` passed / `8` `unimplemented` with `text_models == ['bytes', 'str']`.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0698-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-bytes.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
