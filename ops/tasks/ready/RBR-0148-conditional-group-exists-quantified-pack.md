# RBR-0148: Publish a bounded quantified-conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified-conditional manifest so the queue reopens quantified conditional composition through an exact CPython-supported slice instead of jumping straight to a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_quantified_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose two-arm conditional site is quantified exactly twice, such as `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded capture-present and capture-absent outcomes for that exact shape, including haystacks that require `dd` when the capture is present and `ee` when it is absent.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the conditional is enough, while omitted-no-arm or empty-arm quantified conditionals, replacement semantics, alternation inside the repeated arms, nested conditionals inside the repeated site, ranged or open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0105`, `RBR-0096`, and `RBR-0147`.
- This task exists so the queue reopens quantified conditional composition through one exact accepted slice before broader backtracking-heavy conditional execution is queued.
