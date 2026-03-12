# RBR-0068: Publish a grouped-alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded grouped-alternation manifest so the next frontier after top-level branch selection is explicit before broader nested or quantified regex work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_alternation_workflows.json`
- `tests/conformance/test_correctness_grouped_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated grouped-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one grouped branch-selection site, such as `a(b|c)d` and `a(?P<word>b|c)d`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one capture or named group wrapped by literal prefix/suffix text is enough, while nested groups, multiple alternations, branch-local backreferences, quantified branches, conditionals, and broader backtracking behavior remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0066` and `RBR-0067`.
- This task exists so the worker can expose the next concrete branch-selection gap after top-level alternation without jumping straight to quantifiers, nested groups, or conditionals.
