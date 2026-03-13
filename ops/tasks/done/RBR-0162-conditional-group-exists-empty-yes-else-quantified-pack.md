# RBR-0162: Publish a bounded quantified empty-yes-arm conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified empty-yes-arm conditional manifest so repeated empty-arm composition reaches the queue through an exact CPython-supported slice instead of jumping straight to a broader alternation-heavy or backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_quantified_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_quantified_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified empty-yes-arm conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose empty-yes-arm conditional site is quantified exactly twice, such as `(a(b)?c(?(1)|e)){2}` and `(a(?P<word>b)?c(?(word)|e)){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover bounded repeated capture-present and capture-absent outcomes for that exact shape, including haystacks that require `abcabc` when both captures are present, `aceace` when both are absent, and at least one mixed present/absent repetition that proves the conditional is evaluated per repeated site instead of being cached from the first iteration.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the accepted empty-yes-arm conditional is enough, while fully-empty quantified variants, replacement semantics, alternation inside the repeated else arm, nested conditionals inside the repeated site, deeper nesting, ranged or open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified empty-yes-arm behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0161`, `RBR-0158`, and `RBR-0149`.
- This task exists so the queue reopens repeated empty-yes-arm conditional composition through one exact accepted slice before the alternation-heavy empty-arm follow-ons are even eligible to queue.

## Completion
- Added `conditional_group_exists_empty_yes_else_quantified_workflows.json` and wired it into the default combined correctness publication.
- Published eight bounded quantified empty-yes-arm cases across numbered and named module/`Pattern` paths using a non-capturing repeated wrapper so the numbered optional capture stays addressable as group `1`.
- Regenerated `reports/correctness/latest.json`; the combined scorecard now reports 346 total cases with 338 passes and 8 honest `unimplemented` outcomes for this newly published slice pending `RBR-0163`.
