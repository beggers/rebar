# RBR-0062: Publish a grouped-segment correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded grouped-segment manifest so `rebar` explicitly records the next grouped-execution frontier after bare backreferences: literal text surrounding a single capture group.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_segment_workflows.json`
- `tests/conformance/test_correctness_grouped_segment_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated grouped-segment manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal-segment workflows such as `a(b)c` and `a(?P<word>b)c` on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: a single capture wrapped by literal prefix/suffix text is enough, while nested groups, alternation, quantified groups, interleaved backreferences, and broader parser expansion remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-segment behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0060` and the existing grouped/named correctness manifests.
- This task exists so the worker can expose the next concrete grouped-execution gap without jumping straight to alternation, conditionals, or other broader regex features.
