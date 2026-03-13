# RBR-0165: Publish a bounded quantified fully-empty conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified fully-empty conditional manifest so repeated fully-empty composition reaches the queue through an exact CPython-supported slice instead of jumping straight to a broader alternation-heavy or backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_quantified_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_fully_empty_quantified_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified fully-empty conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose fully-empty conditional site is quantified exactly twice, such as `(a(b)?c(?(1)|)){2}` and `(a(?P<word>b)?c(?(word)|)){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded repeated capture-present and capture-absent outcomes for that exact shape, including haystacks that match as `abcabc` when both captures are present, `acac` when both are absent, and at least one mixed present/absent repetition plus one extra-suffix failure that proves this slice does not silently broaden into the quantified empty-yes-arm spelling.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the accepted fully-empty conditional is enough, while empty-yes-arm quantified variants, replacement semantics, alternation inside the repeated else arm, nested conditionals inside the repeated site, deeper nesting, ranged or open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified fully-empty behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0164`, `RBR-0161`, and `RBR-0149`.
- This task exists so the queue reopens repeated fully-empty conditional composition through one exact accepted slice before the alternation-heavy empty-arm follow-ons are even eligible to queue.

## Completion
- Added `conditional_group_exists_fully_empty_quantified_workflows.json` to the default combined correctness fixture list and published a new 10-case quantified fully-empty manifest covering numbered and named compile, present, absent, mixed, and extra-suffix failure observations for `(?:a(b)?c(?(1)|)){2}` and `(?:a(?P<word>b)?c(?(word)|)){2}`.
- Regenerated `reports/correctness/latest.json`; the combined report now publishes 356 total cases across 49 manifests with 346 passes and 10 honest `unimplemented` outcomes from this new bounded slice.
- Added a focused regression test for the new manifest and refreshed the adjacent quantified empty-yes-arm combined-scorecard assertions to the new totals.
