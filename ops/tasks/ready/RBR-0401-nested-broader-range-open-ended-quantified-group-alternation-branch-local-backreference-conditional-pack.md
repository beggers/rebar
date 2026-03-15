# RBR-0401: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference conditional correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional manifest so the shared branch-local frontier reopens through one exact combined conditional follow-on after `RBR-0399` closed the adjacent plain benchmark slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` that CPython already supports.
- The published cases include a numbered lower-bound same-branch success such as `abbbd` or `accccd`, a numbered mixed-branch or longer-repetition success such as `abcbccd`, at least one numbered no-match such as `abbbe` or `abcbcc` that proves the conditional yes-arm does not rescue a failing replay, one named lower-bound success that keeps `outer` and `inner` observable, one named mixed-branch or longer-repetition compiled-`Pattern.fullmatch()` success that keeps the final selected branch observable, and at least one named no-match that keeps the broader-range open-ended `{2,}` floor honest without widening into deeper nested grouped execution.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper.
- The shared `tests/python/test_branch_local_backreference_parity_suite.py` surface continues to discover published `*branch_local_backreference_workflows.py` fixtures and covers this new manifest through the existing fixture-bundle path instead of adding another manifest-specific parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one broader-range open-ended `{2,}` nested `(b|c)` site followed immediately by one same-branch backreference and one group-exists conditional is enough, while replacement semantics, callable replacements, broader lower bounds, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared branch-local-backreference parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined correctness helpers and shared branch-local-backreference parity suite instead of introducing another frontier-specific harness layer.

## Notes
- Build on `RBR-0399` and the existing shared branch-local-backreference fixture/parity surfaces.
- A direct CPython probe in the current checkout confirms representative numbered and named fullmatches for this exact slice on `abbbd`, `abcbccd`, and `accccd`, while `abbbe` and `abcbcc` remain explicit no-match cases.
- Keep later parity on `tests/python/test_branch_local_backreference_parity_suite.py` and later benchmark catch-up on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` path instead of forking another benchmark family.
