# RBR-0142: Publish a bounded alternation-heavy omitted-no-arm conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded omitted-no-arm conditional manifest that introduces the accepted alternation-heavy no-else spelling through an exact CPython-supported workflow instead of reopening a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_no_else_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_no_else_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated omitted-no-arm alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose omitted-no-arm conditional yes-arm contains one literal alternation site, such as `a(b)?c(?(1)(de|df))` and `a(?P<word>b)?c(?(word)(de|df))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded branch-selection outcomes for that exact shape, including capture-present haystacks that take both alternation arms and capture-absent haystacks that fail because no else arm exists.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one alternation site inside the yes-arm of an omitted-no-arm conditional is enough, while explicit-empty-else or empty-yes-arm variants, replacement semantics, quantified conditionals, nested alternation inside the arms, branch-local backreferences inside the conditional arms, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-heavy conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0141` and the already-landed `RBR-0128` explicit-empty-else alternation slice.
- This task exists so the queue keeps accepted conditional syntax coverage explicit instead of treating omitted-no-arm and explicit-empty-else alternation spellings as interchangeable.
