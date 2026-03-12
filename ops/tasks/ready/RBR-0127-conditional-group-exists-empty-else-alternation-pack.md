# RBR-0127: Publish a bounded alternation-heavy explicit-empty-else conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with one bounded explicit-empty-else conditional manifest that introduces the first alternation-heavy conditional execution slice through an exact CPython-supported workflow instead of reopening a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_else_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_else_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated explicit-empty-else alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose explicit-empty-else conditional yes-arm contains one literal alternation site, such as `a(b)?c(?(1)(de|df)|)` and `a(?P<word>b)?c(?(word)(de|df)|)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded branch-selection outcomes for that exact shape, including capture-present haystacks that take both alternation arms and capture-absent haystacks that succeed through the empty else branch.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one alternation site inside the yes-arm of an explicit-empty-else conditional is enough, while no-else conditionals, empty-yes-arm conditionals, replacement semantics, quantified conditionals, nested alternation inside the arms, branch-local backreferences inside the conditional arms, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-heavy conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0126`.
- This task exists so the queue reopens backtracking through one already-described explicit-empty-else conditional shape instead of jumping straight to broader conditional execution or replacement-conditioned work.
