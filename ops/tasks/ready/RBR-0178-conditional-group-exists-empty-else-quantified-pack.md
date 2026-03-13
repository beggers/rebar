# RBR-0178: Publish a bounded quantified explicit-empty-else conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified explicit-empty-else conditional manifest so the accepted repeated `|)` spelling stays explicit even where its bounded absent-arm runtime overlaps the omitted-no-arm form.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_else_quantified_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_else_quantified_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified explicit-empty-else manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose explicit-empty-else conditional site is quantified exactly twice, such as `a(b)?c(?(1)d|){2}` and `a(?P<word>b)?c(?(word)d|){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded capture-present and capture-absent outcomes for that exact shape, including haystacks that require `dd` when the capture is present, capture-absent haystacks that succeed because the explicit empty else contributes zero width at both repetitions, and compile-path observations that keep the accepted `|)` spelling visible as a distinct syntax slice.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the explicit-empty-else conditional is enough, while omitted-no-arm, two-arm, or empty-arm quantified conditionals, replacement semantics, alternation inside the repeated arm, nested conditionals inside the repeated site, ranged or open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified explicit-empty-else behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0177`, `RBR-0153`, and `RBR-0150`.
- This task exists so the queue records the accepted quantified explicit-empty-else spelling explicitly instead of leaving it as a benchmark-only gap row.
