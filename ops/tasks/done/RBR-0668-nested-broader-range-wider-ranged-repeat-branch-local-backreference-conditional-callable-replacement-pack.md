# RBR-0668: Publish a nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement manifest so the frontier reopens on correctness publication now that `RBR-0665` closed the adjacent non-conditional callable bytes benchmark gap.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows:
  - `a((b|c){1,4})\\2(?(2)d|e)`;
  - `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)`.
- The published rows stay pinned to the same bounded owner shape already established by the adjacent wider `{1,4}` non-conditional callable pack and the existing wider-ranged-repeat grouped-conditional owner:
  - include one numbered lower-bound same-branch callback case such as `module.sub(..., callable_match_group(group=1, suffix="x"), "abbd")`;
  - include one numbered first-match-only or doubled-haystack callback case such as `module.subn(..., callable_match_group(group=2, prefix="<", suffix=">"), "abbbdaccd", 1)` or a compiled-`Pattern` equivalent that keeps the mixed branch explicit;
  - include one named callback case that keeps the broader `{1,4}` `outer` capture observable under replacement, such as `module.sub(..., callable_match_group(group="outer", suffix="x"), "abcbccd")` or a compiled-`Pattern` equivalent on `zzacccccdzz`; and
  - include one named first-match-only or doubled-haystack callback case that keeps the selected `inner` branch observable, such as `module.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "abbbdaccd", 1)` or a compiled-`Pattern` equivalent on `zzacccccdabbbdzz`.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- `python/rebar_harness/correctness.py` and `tests/python/test_fixture_parity_support_contract.py` register the new manifest on the shared `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` surface instead of adding another manifest-local selector or parity module.
- `tests/python/test_callable_replacement_parity_suite.py` keeps the new manifest on the existing shared callable surface and leaves it explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- `tests/conformance/correctness_expectations.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1334` total / `1334` passed / `0` `unimplemented` across `111` manifests to `1342` total / `1334` passed / `8` `unimplemented` across `112` manifests; and
  - the new manifest publishes `8` total `str` cases with honest `unimplemented` outcomes rather than disappearing from the scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0668-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new callable-replacement behavior just to make the new cases pass.
- Do not broaden into bytes, Rust-backed parity, benchmark rows, replacement-template variants, broader callback semantics, deeper grouped execution, or another branch-local-backreference family in this run.
- Reuse the existing `callable_match_group` helper and shared callable parity surface instead of adding another manifest-specific harness layer or a new benchmark family.

## Notes
- `RBR-0668` is the next available feature task id in the current checkout; `RBR-0667` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0665` so the broader `{1,4}` non-conditional callable bytes benchmark catch-up closes before the adjacent broader `{1,4}` conditional callable publication reopens correctness work on the same shared nested-group callback frontier.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` already pins the exact broader `{1,4}` numbered and named module and compiled-`Pattern` callable owner shapes for `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py` already pins the adjacent wider `{1,4}` grouped-conditional owner shape on the same counted-repeat frontier, so this callable publication can stay on existing owner paths without another synthesis pass;
  - `python/rebar_harness/correctness.py` and `tests/python/test_fixture_parity_support_contract.py` currently publish the wider `{1,4}` non-conditional callable manifest plus the broader-range open-ended `{2,}` conditional callable manifest, but no wider `{1,4}` conditional callable sibling;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the wider `{1,4}` non-conditional callable rows plus the broader-range open-ended `{2,}` conditional callable rows, but no wider `{1,4}` conditional callable rows, so a later benchmark catch-up can stay on the same manifest path; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run raise `NotImplementedError` for `rebar.sub(...)` and `rebar.subn(...)` on `a((b|c){1,4})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)`, so this publication pack is not a stale no-op.

## Completion Notes
- 2026-03-19: Added the new shared-surface `str`-only callable-replacement fixture at `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`, registered it on `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`, and marked all 8 new cases as explicitly pending in `tests/python/test_callable_replacement_parity_suite.py`.
- Republished `reports/correctness/latest.py`; the tracked combined report now shows `1342` total / `1334` passed / `8` unimplemented across `112` manifests, and the new manifest contributes `8` `str` cases with honest `unimplemented` outcomes.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py --report .rebar/tmp/rbr-0668-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
