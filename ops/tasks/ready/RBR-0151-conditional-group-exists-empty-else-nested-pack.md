# RBR-0151: Publish a bounded nested explicit-empty-else conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded nested explicit-empty-else conditional manifest so the queue keeps accepted nested conditional composition explicit before empty-yes-arm or fully-empty nested variants reopen the frontier.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_else_nested_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_else_nested_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested explicit-empty-else conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose explicit-empty-else conditional yes-arm contains one nested explicit-empty-else conditional site, such as `a(b)?c(?(1)(?(1)d)|)` and `a(?P<word>b)?c(?(word)(?(word)d)|)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded success and failure outcomes for that exact shape, including capture-present haystacks that require the nested `d` suffix and capture-absent haystacks that still match because the outer explicit empty else contributes nothing.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested explicit-empty-else conditional site inside the outer yes-arm is enough, while replacement semantics, omitted-no-arm or empty-yes-arm nested variants, alternation inside the nested arms, quantified conditionals, deeper nesting, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested explicit-empty-else behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0111`, `RBR-0147`, and the already-landed explicit-empty-else baseline.
- This task exists so the queue keeps accepted nested conditional syntax explicit instead of jumping straight from one omitted-no-arm nested slice to broader backtracking-heavy composition.
