# RBR-0186: Publish a bounded alternation-heavy two-arm conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded alternation-heavy two-arm conditional manifest so broader backtracking-heavy conditional execution reopens through an explicit published slice instead of a vague frontier jump.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated alternation-heavy two-arm conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose yes and else arms each contain one small literal alternation site, such as `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded observed outcomes for that exact shape, including capture-present haystacks that select both `de` and `df`, capture-absent haystacks that select both `eg` and `eh`, and compile-path observations that keep the two-arm alternation spelling visible as a distinct syntax slice.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one alternation site per arm is enough, while replacement semantics, quantified repeats, nested conditionals inside either arm, branch-local backreferences inside the alternations, ranged/open-ended repetition, and broader backtracking-heavy shapes remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-heavy two-arm conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0185`, `RBR-0182`, and `RBR-0174`.
- This task exists so the queue reopens broader conditional execution through one exact two-arm alternation slice instead of an underspecified backtracking bucket.

## Completion
- Added `conditional-group-exists-alternation-workflows` to the default correctness publication set with 10 bounded numbered/named cases covering compile metadata plus both yes-arm (`de`, `df`) and else-arm (`eg`, `eh`) alternation outcomes across module and compiled-pattern paths.
- Added a regression test that verifies the combined scorecard includes the new suite and records the current slice honestly as `10` `unimplemented` cases rather than dropping it from publication.
- Republished `reports/correctness/latest.json`; the combined published scorecard now reports `406` total cases across `55` manifests with `396` passes and `10` explicit `unimplemented` outcomes.
