# RBR-0071: Publish a grouped-alternation replacement correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded grouped-alternation replacement manifest so the next combined capture-and-replacement frontier is explicit before nested groups, quantified branches, or broader template parsing work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_alternation_replacement_workflows.json`
- `tests/conformance/test_correctness_grouped_alternation_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated grouped-alternation replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows with one grouped alternation site, such as `sub()` or `subn()` using `a(b|c)d` with `\\1x` and `a(?P<word>b|c)d` with `\\g<word>x`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one grouped branch-selection site feeding a replacement template is enough, while callable replacement semantics for alternation groups, branch-local backreferences, nested groups, quantified branches, multiple alternations, and broader template parsing remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0069` and `RBR-0070`.
- This task exists so the worker can expose the next concrete workflow gap after grouped alternation without jumping straight to nested groups, quantified branches, or broader replacement-template parsing.
