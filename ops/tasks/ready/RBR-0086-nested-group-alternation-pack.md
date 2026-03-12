# RBR-0086: Publish a nested-group alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded nested-group alternation manifest so the next combined nesting-and-alternation frontier is explicit before quantified branches, branch-local backreferences, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_workflows.json`
- `tests/conformance/test_correctness_nested_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one nested capture site whose inner group contains a single literal alternation, such as `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capturing group containing one inner numbered or named capturing group with one literal alternation site is enough, while multiple alternations, quantified branches, branch-local backreferences, replacement-template behavior, callable replacement behavior, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0078`, `RBR-0070`, and `RBR-0085`.
- This task exists so the worker can expose the next concrete compatibility gap after bounded nested-group callable replacement without jumping straight to quantified branches, branch-local backreferences, or broader backtracking semantics.
