# RBR-0181: Publish a bounded nested two-arm conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded nested two-arm conditional manifest so the remaining `conditional_group_exists_boundary` gap becomes explicit published behavior instead of lingering only as a benchmark hole.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_nested_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_nested_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested two-arm conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose outer two-arm conditional yes-arm contains one nested two-arm conditional site, such as `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded observed outcomes for that exact shape, including capture-present haystacks that require the nested `d` suffix and capture-absent haystacks that select the outer `f` arm.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested two-arm conditional site inside the outer yes-arm is enough, and this task must not broaden the group structure just to make the inner `e` arm dynamically reachable.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested two-arm conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0174`, `RBR-0147`, and `RBR-0153`.
- This task exists so accepted nested two-arm conditional composition reaches the published correctness surface before broader backtracking-heavy conditional execution is queued.
