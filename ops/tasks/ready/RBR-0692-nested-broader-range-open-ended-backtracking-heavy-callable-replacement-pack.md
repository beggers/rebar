# RBR-0692: Publish the nested broader-range open-ended backtracking-heavy callable-replacement pair

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the existing shared callable-replacement correctness publication with one exact broader-range open-ended `{2,}` nested grouped backtracking-heavy `str` pair, so the frontier reopens on the tracked correctness path before Rust-backed parity, bytes mirrors, or later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py` is the only correctness manifest for this new slice and publishes only these 8 `str` callable-replacement workflows for the exact bounded pattern pair:
  - `a(((bc|b)c){2,})d` through `callable_match_group` on groups `1` or `3`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The new cases stay pinned to one exact broader-range open-ended `{2,}` backtracking-heavy callable surface on the shared correctness path:
  - numbered `module.sub(..., callable_match_group(group=1, suffix="x"), "abcbcd")`;
  - numbered `module.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "abccbccdabcbcd", 1)`;
  - numbered compiled `Pattern.sub(..., callable_match_group(group=1, suffix="x"), "zzabccbcdzz")`;
  - numbered compiled `Pattern.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "zzabcbcbcbcdabccbccdzz", 1)`;
  - named `module.sub(..., callable_match_group(group="outer", suffix="x"), "abccbcd")`;
  - named `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "abccbccdabcbcd", 1)`;
  - named compiled `Pattern.sub(..., callable_match_group(group="outer", suffix="x"), "zzabcbcbcbcdzz")`;
  - named compiled `Pattern.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "zzabcbcbcbcdabccbccdzz", 1)`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps this work on the existing shared callable owner surface:
  - add one manifest spec for `nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows` with exactly the 8 published `str` case ids, the two `str` compile patterns above, `CALLABLE_STR_ONLY_OPERATION_HELPER_COUNTS`, and `expected_text_models == {"str"}`;
  - if live `rebar` still reports placeholder behavior for any of those new cases, represent them through `pending_rebar_case_ids` instead of inventing a detached parity suite, helper shim, or bytes-only owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1366` total / `1366` passed / `0` `unimplemented` across `113` manifests to `1374` total across `114` manifests, with the new 8-case slice reported as either passing or `unimplemented` according to the live `rebar` result;
  - `collection.replacement.nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy.callable` publishes `8` total `str` cases on the combined scorecard.
- The new slice is reported honestly as `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the publication or force-marked as parity.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py --report .rebar/tmp/rbr-0692-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-pack.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new open-ended callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes mirrors, Rust-backed parity, benchmark rows, replacement-template flows, branch-local-backreference follow-ons, or another grouped family in this run.
- Keep any later parity follow-on anchored to `tests/python/test_callable_replacement_parity_suite.py` and any later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path.

## Notes
- `RBR-0692` is the next available feature task id in the current checkout; `RBR-0691` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after the drained `RBR-0690` head so the nested grouped backtracking-heavy callable frontier reopens through one exact broader-range open-ended `{2,}` correctness follow-on instead of jumping to bytes mirrors, benchmark work, or another replacement family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0690-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-benchmark-catch-up.md` records that the adjacent broader `{1,4}` nested backtracking-heavy callable bytes slice is fully caught up on the shared Python-path benchmark surface, so the next bounded step is the next nearby correctness publication rather than more work on the closed `{1,4}` pair;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py` already anchors the same nested backtracking-heavy callable family at `{1,4}`, while `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py` already anchors the adjacent `{2,}` backtracking-heavy haystack family on the non-callable correctness path;
  - direct `rg` probes in this planning run confirmed that `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py` does not exist yet and that `tests/python/test_callable_replacement_parity_suite.py` currently contains no manifest owner entry for an open-ended nested backtracking-heavy callable slice; and
  - `reports/correctness/latest.py` currently publishes `1366` total / `1366` passed / `0` `unimplemented` across `113` manifests, so this task will reopen the tracked correctness frontier through one exact new manifest instead of retiring stale work.
