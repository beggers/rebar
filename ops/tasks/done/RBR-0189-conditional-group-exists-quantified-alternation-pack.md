# RBR-0189: Publish a bounded quantified alternation-heavy two-arm conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified alternation-heavy two-arm conditional manifest so quantified composition follows the reopened two-arm alternation frontier through an exact CPython-supported slice instead of a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_quantified_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified alternation-heavy two-arm conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose two-arm conditional site contains one small literal alternation in each arm and is quantified exactly twice, such as `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded observed outcomes for that exact shape, including capture-present haystacks that force both repeated yes-arm alternation branches and capture-absent haystacks that force both repeated else-arm alternation branches.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over this exact alternation-heavy two-arm conditional site is enough, while replacement semantics, nested conditionals inside either repeated arm, ranged or open-ended repeats, branch-local backreferences inside the alternations, and broader backtracking-heavy shapes remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified alternation-heavy conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0188`, `RBR-0150`, and `RBR-0129`.
- This task exists so quantified composition resumes through one exact alternation-heavy two-arm follow-on instead of an underspecified broader-backtracking frontier.
- Completed 2026-03-13: added `conditional-group-exists-quantified-alternation-workflows` to the default correctness fixture set, published the new 10-case numbered/named `{2}` alternation-heavy two-arm conditional manifest, added a focused harness regression test, and republished `reports/correctness/latest.json` at 416 total cases with 10 honest `unimplemented` outcomes pending `RBR-0190`.
