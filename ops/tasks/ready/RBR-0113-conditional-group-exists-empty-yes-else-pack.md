# RBR-0113: Publish a bounded conditional empty-yes-arm correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded conditional manifest for the CPython-accepted empty-yes-arm group-exists shape so the queue keeps broadening accepted conditional runtime syntax instead of jumping straight to rejected-syntax diagnostics.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows where an already-open optional numbered or named capture controls a conditional with an explicit empty yes arm and a literal else arm, such as `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover both the group-present and group-omitted outcomes for that exact empty-yes-arm shape, including the observable zero-width success when the capture is present and the else-arm match path when it is absent.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one conditional site keyed by an already-open group with an explicit empty yes arm is enough, while fully empty `(?(1)|)` / `(?(name)|)` forms, assertion-tested conditionals, nested conditionals, conditional replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0112`.
- This task exists so the worker publishes the next exact CPython-accepted conditional runtime shape instead of stopping the queue at explicit-empty-else syntax.
