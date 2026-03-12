# RBR-0065: Publish a bounded literal-alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded literal-alternation manifest so the next post-segment execution frontier is explicit before broader grouped or conditional regex work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/literal_alternation_workflows.json`
- `tests/conformance/test_correctness_literal_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated literal-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny top-level literal alternation workflows such as `ab|ac` on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one simple top-level literal alternation path is enough, while grouped alternation, nested branches, quantified branches, conditionals, and broader backtracking behavior remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0063` and `RBR-0064`.
- This task exists so the worker can expose the next concrete branch-selection gap without jumping straight to grouped alternation, conditionals, or broader regex features.
