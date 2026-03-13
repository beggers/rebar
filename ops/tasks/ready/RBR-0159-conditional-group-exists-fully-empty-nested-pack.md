# RBR-0159: Publish a bounded nested fully-empty conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded nested fully-empty conditional manifest so the queue keeps accepted nested empty-arm composition explicit after the narrower nested empty-yes-arm slice lands.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_nested_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_fully_empty_nested_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested fully-empty conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose outer empty-yes-arm conditional else-arm contains one nested fully-empty conditional site, pinned to patterns such as `a(b)?c(?(1)|(?(1)|))` and `a(?P<word>b)?c(?(word)|(?(word)|))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded success and failure outcomes for that exact shape, including capture-present haystacks that match because the outer yes-arm succeeds at zero width, capture-absent haystacks that match because the nested fully-empty branch contributes no suffix, and at least one extra-suffix failure that proves this slice does not silently broaden into the nested empty-yes-arm spelling.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested conditional site inside the outer else-arm is enough, while replacement semantics, nested explicit-empty-else or empty-yes-arm follow-ons beyond the already-landed bounded slice, alternation-heavy nested arms, quantified conditionals, deeper nesting, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested fully-empty behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0155` and `RBR-0158`.
- This task exists so the queue keeps accepted nested fully-empty syntax explicit instead of jumping from the narrower nested empty-yes-arm slice to broader nested empty-arm or backtracking-heavy composition.
