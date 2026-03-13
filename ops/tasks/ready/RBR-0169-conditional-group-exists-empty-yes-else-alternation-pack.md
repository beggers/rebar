# RBR-0169: Publish a bounded alternation-heavy empty-yes-arm conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded empty-yes-arm conditional manifest whose else arm contains a single literal alternation site, so the first broader empty-yes-arm execution shape becomes explicit once `RBR-0168` has corrected the benchmark contracts.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated empty-yes-arm alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose empty-yes-arm conditional else arm contains one literal alternation site, such as `a(b)?c(?(1)|(e|f))` and `a(?P<word>b)?c(?(word)|(e|f))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded branch-selection outcomes for that exact shape, including capture-present haystacks that succeed through the empty yes arm and capture-absent haystacks that take both alternation arms.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one alternation site inside the else arm of an empty-yes-arm conditional is enough, while explicit-empty-else or omitted-no-arm variants, replacement semantics, quantified conditionals, nested conditionals, wider alternation-bearing arms, branch-local backreferences inside the conditional arms, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-heavy conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0168`, `RBR-0158`, and `RBR-0129`.
- This task exists so the queue reopens broader empty-yes-arm execution through one exact accepted slice instead of jumping straight to a vague backtracking bucket.
