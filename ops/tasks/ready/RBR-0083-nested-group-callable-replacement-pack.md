# RBR-0083: Publish a nested-group callable-replacement correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded nested-group callable-replacement manifest so the next combined nesting-and-callback frontier is explicit before quantified branches, branch-local backreferences, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_callable_replacement_workflows.json`
- `tests/conformance/test_correctness_nested_group_callable_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded callable replacement observations through the public `rebar` API for tiny literal workflows with one capture nested inside another, such as `sub()` or `subn()` using `a((b))d` with a callable that reads `match.group(1)` or `match.group(2)`, and `a(?P<outer>(?P<inner>b))d` with a callable that reads `match.group("outer")` or `match.group("inner")`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested capture site inside literal prefix/suffix text feeding a callable replacement is enough, while nested alternation, quantified groups, replacement-template behavior beyond the exact callable inputs, branch-local backreferences, broader match-object callback semantics, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0078`, `RBR-0081`, and `RBR-0082`.
- This task exists so the worker can expose the next concrete gap after bounded nested-group replacement-template parity without jumping straight to quantified branches, branch-local backreferences, or broader callback semantics.
