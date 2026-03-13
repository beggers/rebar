# RBR-0156: Publish a bounded nested empty-yes-arm conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded nested empty-yes-arm conditional manifest so the queue keeps accepted nested empty-arm composition explicit before nested fully-empty conditionals or broader backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_nested_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_nested_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested empty-yes-arm conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose outer empty-yes-arm conditional else-arm contains one nested conditional site, pinned to patterns such as `a(b)?c(?(1)|(?(1)e|f))` and `a(?P<word>b)?c(?(word)|(?(word)e|f))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded success and failure outcomes for that exact shape, including capture-present haystacks that match because the outer yes-arm succeeds at zero width, capture-absent haystacks that match because the nested else-arm selects `f`, and at least one capture-absent failure that proves the nested `e` arm is not taken when the group is missing.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested conditional site inside the outer else-arm is enough, while replacement semantics, nested fully-empty variants, explicit-empty-else or omitted-no-arm nested follow-ons, alternation-heavy nested arms, quantified conditionals, deeper nesting, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested empty-yes-arm behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0155` and the already-landed empty-yes-arm baseline.
- This task exists so the queue keeps accepted nested empty-yes-arm syntax explicit instead of jumping from nested explicit-empty-else directly to broader nested empty-arm or backtracking-heavy composition.
