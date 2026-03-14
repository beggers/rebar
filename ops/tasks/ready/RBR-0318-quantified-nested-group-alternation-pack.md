# RBR-0318: Publish a quantified nested-group alternation correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded quantified nested-group alternation manifest so the next combined quantified-nesting-and-branch-selection frontier is explicit after `RBR-0316` catches the adjacent callable-replacement slice up on the benchmark surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_nested_group_alternation_workflows.py`
- `tests/conformance/test_correctness_quantified_nested_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified nested-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile, module-search, and compiled-`Pattern` fullmatch observations through the public `rebar` API for quantified nested captures on `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`, using numbered and named cases that CPython already supports.
- The published cases cover at least one lower-bound one-branch path such as `abd`, one repeated-branch path such as `abccd` or `acbbd`, and one named-path case that keeps the quantified outer capture plus final inner branch observable under repetition.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture containing one `+`-quantified inner numbered or named capture with one literal alternation site is enough, while callable replacement, replacement-template behavior, broader counted repeats like `{1,4}` or `{1,}`, branch-local backreferences, deeper nested grouped execution, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified nested-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Queue this immediately behind `RBR-0316` so benchmark catch-up for the callable slice lands before the next correctness frontier reopens.
- Build on `RBR-0087` and the existing quantified nested-group fixture helpers.
- Keep later parity and benchmark follow-ons on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path, which already carries the quantified nested-group alternation gap anchor instead of forking another benchmark family.
