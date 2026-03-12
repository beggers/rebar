# RBR-0136: Publish a bounded empty-yes-arm conditional replacement correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded empty-yes-arm conditional replacement manifest so the queue keeps accepted conditional replacement work concrete before fully-empty replacement-conditioned work or broader backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated empty-yes-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows using `sub()` and `subn()` with simple replacement strings on `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)` through module and compiled-`Pattern` entrypoints that CPython already supports.
- The published cases cover both capture-present and capture-absent paths for that exact empty-yes-arm conditional replacement shape.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one empty-yes-arm conditional site feeding constant replacement text is enough, while explicit-empty-else or fully-empty variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0114`, `RBR-0115`, and `RBR-0135`.
- This task exists so the queue reopens after `RBR-0135` with the next exact accepted conditional-replacement gap instead of jumping straight to fully-empty replacement, nested conditionals, quantified conditionals, or a vague broader-backtracking bucket.
