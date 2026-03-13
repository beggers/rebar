# RBR-0172: Publish a bounded alternation-bearing fully-empty conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded fully-empty conditional manifest whose else arm contains an explicit zero-width alternation site, so the accepted alternation-bearing fully-empty spelling becomes explicit once `RBR-0168` has corrected the benchmark contracts.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_alternation_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_fully_empty_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated fully-empty alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose fully-empty conditional else arm contains an explicit zero-width alternation spelling, such as `a(b)?c(?(1)|(?:|))` and `a(?P<word>b)?c(?(word)|(?:|))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded capture-present and capture-absent outcomes for that exact shape, plus at least one suffix-failure observation that proves this slice does not silently broaden into the empty-yes-arm alternation spelling.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one explicit zero-width alternation site inside the else arm of a fully-empty conditional is enough, while empty-yes-arm alternation, replacement semantics, quantified conditionals, nested conditionals, wider alternation-bearing arms, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-bearing conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0168`, `RBR-0161`, and `RBR-0141`.
- This task exists so the queue records the accepted alternation-bearing fully-empty spelling explicitly even though its bounded runtime overlaps the already-landed fully-empty slice.
