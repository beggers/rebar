# RBR-0074: Publish a grouped-alternation callable-replacement correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded grouped-alternation callable-replacement manifest so the next combined alternation-and-callback frontier is explicit before nested groups, quantified branches, or broader callback semantics reopen the queue.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_alternation_callable_replacement_workflows.json`
- `tests/conformance/test_correctness_grouped_alternation_callable_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated grouped-alternation callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded callable replacement observations through the public `rebar` API for tiny literal workflows with one grouped alternation site, such as `sub()` or `subn()` using `a(b|c)d` with a callable that reads `match.group(1)` and `a(?P<word>b|c)d` with a callable that reads `match.group("word")`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one grouped branch-selection site feeding a callable replacement is enough, while broader match-object methods, branch-local backreferences, nested groups, quantified branches, multiple alternations, and general callback semantics remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0072` and `RBR-0073`.
- This task exists so the worker can expose the next concrete workflow gap after grouped-alternation replacement-template parity without jumping straight to nested groups, quantified branches, or broader callback semantics.
