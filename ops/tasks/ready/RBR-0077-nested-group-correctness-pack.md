# RBR-0077: Publish a nested-group correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded nested-group manifest so the next frontier after grouped-alternation callable replacement becomes explicit before quantified branches, branch-local backreferences, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_workflows.json`
- `tests/conformance/test_correctness_nested_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one capture nested inside another, such as `a((b))d` and `a(?P<outer>(?P<inner>b))d`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested capture site inside literal prefix/suffix text is enough, while nested alternations, quantified groups, branch-local backreferences, replacement-template behavior, callable replacement behavior, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0051`, `RBR-0053`, `RBR-0063`, and `RBR-0076`.
- This task exists so the worker can reopen the correctness frontier with bounded nesting, which combines already-supported grouping semantics without jumping straight to quantified branches or broader backtracking.
