# RBR-0336: Publish a nested broader-range wider-ranged-repeat quantified-group alternation plus branch-local-backreference correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference manifest so the frontier reopens on the existing nested-group alternation anchor once `RBR-0334` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` that CPython already supports.
- The published cases include lower-bound same-branch successes such as `abbd` and `accd`, broader counted-repeat successes such as `abbbd` or `abcbccd`, plus explicit no-match observations such as `abcd`, `abcbcd`, or a fifth-repetition overflow that proves the `{1,4}` envelope stays bounded.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke subprocess wrapper.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader `{1,4}` `(b|c)` site immediately replayed by one same-branch backreference is enough, while open-ended counted repeats, replacement semantics, conditionals, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared scorecard expectations, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined correctness scorecard helpers and expectation tables instead of introducing another frontier-specific harness layer.

## Notes
- Build on `RBR-0332` and the queued `RBR-0334` benchmark catch-up.
- Keep later parity and benchmark catch-up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path instead of forking another benchmark family for the same bounded nested-group alternation frontier.
