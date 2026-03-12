# RBR-0116: Publish a bounded conditional fully-empty correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded conditional manifest for the CPython-accepted fully-empty group-exists shape so the queue keeps broadening accepted conditional runtime syntax instead of jumping straight to rejected-syntax diagnostics.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_fully_empty_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows where an already-open optional numbered or named capture controls a conditional with fully empty yes and else arms, such as `a(b)?c(?(1)|)` and `a(?P<word>b)?c(?(word)|)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover both the group-present and group-omitted outcomes for that exact fully-empty shape, including the observable zero-width success in both branches and the preserved match-object group values from the optional capture.
- The pack makes the syntax distinction explicit: it should document the accepted `(|)` spelling as a separate reported surface even though the bounded runtime behavior is degenerate.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one conditional site keyed by an already-open group with fully empty yes and else arms is enough, while assertion-tested conditionals, nested conditionals, conditional replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0115`.
- This task exists so the worker publishes the next exact CPython-accepted conditional syntax surface instead of stopping the queue at empty-yes-arm coverage.

## Completion
- Added `conditional_group_exists_fully_empty_workflows.json` as a dedicated six-case manifest for numbered and named `(?(1)|)` / `(?(name)|)` module and compiled-pattern observations.
- Extended `python/rebar_harness/correctness.py` so the fully empty conditional manifest is part of the default combined correctness publication set.
- Added `test_correctness_conditional_group_exists_fully_empty_workflows.py` and republished `reports/correctness/latest.json`; the combined scorecard now reports 218 total published cases with the new fully empty conditional slice recorded honestly as 6 `unimplemented` cases against CPython success observations.
