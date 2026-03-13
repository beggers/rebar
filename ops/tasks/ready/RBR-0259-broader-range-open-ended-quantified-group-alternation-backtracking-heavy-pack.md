# RBR-0259: Publish a broader-range open-ended quantified-group alternation backtracking-heavy correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended grouped backtracking-heavy manifest so the grouped frontier widens the overlapping-branch `{2,}` slice immediately after the broader-range grouped-conditional trio.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended grouped backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|b)c){2,}d` and `a(?P<word>(bc|b)c){2,}d` that CPython already accepts.
- The published cases include lower-bound successes through both overlapping branches such as `abcbcd` and `abcbccd`, mixed-branch successes such as `abccbcd` and one bounded fourth-repetition success, plus explicit no-match observations like `abcd` or a haystack whose branch choices fail before the trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{2,}` envelope around one overlapping `(bc|b)c` site is enough, while conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range grouped backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0258`.
- This task exists so the queue widens the overlapping-branch grouped frontier through one exact broader-range open-ended slice instead of pausing after the grouped-conditional trio.
