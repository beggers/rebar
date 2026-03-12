# RBR-0059: Publish a numbered-backreference correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard past the grouped/named benchmark catch-up with a bounded numbered-backreference manifest so the next grouped-reference frontier stays explicit before broader syntax work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/numbered_backreference_workflows.json`
- `tests/conformance/test_correctness_numbered_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows beyond the named-backreference and grouped/named benchmark frontier by adding a dedicated numbered-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered-backreference observations through the public `rebar` API for tiny literal workflows, including exact compile or match cases such as `(ab)\\1` on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one simple numbered-backreference literal path is enough, while nested references, alternation-driven backreference semantics, conditional groups, and broader backtracking behavior remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed numbered-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0057` and `RBR-0058`.
- This task exists so the worker keeps extending explicit compatibility coverage after the grouped/named benchmark catch-up instead of ending the queue on a measurement-only task.
