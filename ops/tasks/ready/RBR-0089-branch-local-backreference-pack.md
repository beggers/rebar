# RBR-0089: Publish a bounded branch-local backreference correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded branch-local backreference manifest so the next combined alternation-and-backreference frontier is explicit before quantified branches or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/branch_local_backreference_workflows.json`
- `tests/conformance/test_correctness_branch_local_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated branch-local backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows where one alternation branch introduces a capture that is later referenced, such as `a((b)|c)\\2d` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)d`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one alternation site with one branch-local capture/backreference dependency inside literal prefix/suffix text is enough, while quantified branches, nested alternation beyond the exact shapes above, replacement-template behavior, callable replacement behavior, conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed branch-local backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0060`, `RBR-0087`, and `RBR-0088`.
- This task exists so the worker can expose the next concrete gap after bounded nested-group alternation without jumping straight to quantified branches or broader backtracking semantics.
