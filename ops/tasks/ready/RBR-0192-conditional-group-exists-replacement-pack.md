# RBR-0192: Publish a bounded two-arm conditional replacement correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with a bounded two-arm conditional replacement manifest so the queue combines an already-landed two-arm conditional slice with already-landed replacement helpers before broader replacement-conditioned backtracking work reopens the frontier.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated two-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows using `sub()` and `subn()` with simple replacement strings on `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` through module and compiled-`Pattern` entrypoints that CPython already supports.
- The published cases cover both capture-present and capture-absent outcomes for that exact two-arm conditional replacement shape, including bounded workflows whose matched span differs because the yes arm contributes `d` while the else arm contributes `e`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one two-arm conditional site feeding constant replacement text is enough, while replacement templates that read capture groups, callable replacement semantics, alternation-heavy arms, nested conditionals, quantified conditionals, branch-local backreferences inside either arm, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0106`, `RBR-0141`, and the existing literal replacement-helper boundary.
- This task exists so the queue reopens after `RBR-0191` with the smallest remaining two-arm replacement-conditioned gap instead of jumping directly to alternation-heavy replacement branches, deeper nested replacement-conditioned flows, or a vague broader-backtracking bucket.
