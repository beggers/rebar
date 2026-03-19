# RBR-0674: Publish the nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the existing broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement correctness publication with the exact bytes pair on the shared callable parity surface, so the frontier reopens on the tracked correctness path before Rust-backed bytes parity and later Python-path benchmark catch-up land.

## Deliverables
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py` remains the only correctness manifest for this slice and grows only by the 8 byte-typed counterparts to the already-published `str` cases for:
  - `rb"a((b|c){1,4})\\2(?(2)d|e)"` through `callable_match_group` on groups `1` or `2`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"` through `callable_match_group` on groups `"outer"` or `"inner"`.
- The added bytes cases stay pinned to the exact broader `{1,4}` conditional callable-replacement observations already published for the `str` slice:
  - numbered `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbd")`, numbered `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, numbered compiled `Pattern.sub(..., b"zzabcbccdzz")`, and numbered compiled `Pattern.subn(..., b"zzaccdabcbccdzz", 1)`;
  - named `module.sub(..., callable_match_group(group="outer", suffix=b"x"), b"abcbccd")`, named `module.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`, named compiled `Pattern.sub(..., b"zzacccccdzz")`, and named compiled `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccccdabbbdzz", 1)`.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the shared callable-replacement owner honest after this manifest becomes mixed `str`/`bytes`, updates `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` from 8 `str` rows to 16 mixed rows with helper counts growing from `2` to `4` for each of `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`, and keeps the new bytes rows explicit on the shared suite:
  - if the live `rebar` result still reports placeholder behavior for those bytes rows, represent them through `pending_rebar_case_ids` instead of forcing them through the current compile, no-match, near-miss, or return-type-error partitions; and
  - if the live `rebar` result already matches CPython for those bytes rows, keep the mixed-text manifest landed without adding a bytes-only callable suite or another manifest-specific parity module.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1342` total / `1342` passed / `0` `unimplemented` across `112` manifests to `1350` / `1342` / `8` across the same `112` manifests; and
  - `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` moves from `8` total / `8` passed / `0` `unimplemented` with `['str']` text models to `16` total with mixed `str`/`bytes` coverage.
- The new bytes cases are reported honestly as either `pass` or `unimplemented` according to the live `rebar` result rather than being dropped from the published scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0674-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new bytes callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes parity, bytes benchmark rows, replacement-template flows, broader callback semantics, another branch-local-backreference family, or deeper grouped execution in this run.
- Keep the future parity follow-on anchored to the existing `tests/python/test_callable_replacement_parity_suite.py` surface and the later benchmark follow-on on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path.

## Notes
- `RBR-0674` is the next available feature task id in the current checkout; `RBR-0673` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0672` so the broader `{1,4}` conditional callable benchmark catch-up closes before the adjacent bytes publication reopens correctness work on the same shared nested-group callable frontier.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py` currently contains the 8 published `str` rows for this manifest and no bytes rows;
  - `tests/python/test_callable_replacement_parity_suite.py` currently treats that manifest as `str`-only with `len(bundle.cases) == 8`, `text_models == {'str'}`, and helper counts of `2` each for `module_call/sub`, `module_call/subn`, `pattern_call/sub`, and `pattern_call/subn`;
  - `reports/correctness/latest.py` currently publishes `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional.callable` at `8` total / `8` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1342` total / `1342` passed / `0` `unimplemented` across `112` manifests; and
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already publishes the four adjacent `str` benchmark rows for this exact slice on the shared callable owner path after `RBR-0672`, so later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- A later parity follow-on should convert the same bytes pair behind `rebar._rebar` on the existing shared callable parity surface before the benchmark surface mirrors the four adjacent `str` rows already published on `benchmarks/workloads/nested_group_callable_replacement_boundary.py`.
