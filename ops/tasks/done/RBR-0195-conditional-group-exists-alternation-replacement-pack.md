# RBR-0195: Publish a bounded alternation-heavy two-arm conditional replacement correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with a bounded alternation-heavy two-arm conditional replacement manifest so replacement-conditioned work reopens through one explicit alternation-heavy follow-on instead of a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_alternation_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_alternation_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated alternation-heavy two-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows using constant replacement text on `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` through module and compiled-`Pattern` `sub()` and `subn()` entrypoints that CPython already supports.
- The published cases cover both capture-present and capture-absent outcomes for that exact alternation-heavy replacement shape, including bounded workflows that force both yes-arm branches (`de`, `df`) and both else-arm branches (`eg`, `eh`) before replacement text is emitted.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one small literal alternation site in each conditional arm feeding constant replacement text is enough, while replacement templates that read capture groups, callable replacement semantics, quantified repeats, nested conditionals, branch-local backreferences inside the alternations, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed alternation-heavy conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0188`, `RBR-0194`, and the existing conditional replacement helper surface.
- This task exists so the queue reopens after `RBR-0194` with the smallest remaining alternation-heavy replacement-conditioned gap instead of jumping directly to nested replacement-conditioned flows, quantified replacement-conditioned conditionals, or a vague broader-backtracking bucket.

## Completion
- Added `conditional-group-exists-alternation-replacement-workflows` to the default correctness manifest set with eight bounded `sub()`/`subn()` module and compiled-pattern cases for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports 58 manifests and 432 total cases, with the new alternation-heavy conditional replacement suite recorded honestly as 8 `unimplemented` outcomes pending `RBR-0196`.
- Added a focused regression test for the new manifest and refreshed the existing full-suite conditional workflow regressions so they track the new combined report totals and module-workflow summary.
