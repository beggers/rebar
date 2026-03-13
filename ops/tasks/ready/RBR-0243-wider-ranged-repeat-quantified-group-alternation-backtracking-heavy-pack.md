# RBR-0243: Publish a bounded wider ranged-repeat quantified-group alternation backtracking-heavy correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded grouped backtracking-heavy manifest so the queue reopens overlapping-branch grouped alternation through an already-anchored `{1,3}` counted-repeat slice before open-ended grouped-conditionals resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated wider ranged-repeat grouped backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|b)c){1,3}d` and `a(?P<word>(bc|b)c){1,3}d` that CPython already accepts.
- The published cases include lower-bound successes through both overlapping branches such as `abcd` and `abccd`, repeated and mixed-branch successes such as `abcbcd`, `abcbccd`, `abccbcd`, or one bounded third-repetition success, plus explicit no-match observations like `abcccd` or a haystack whose branch choices fail before the trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,3}` envelope around one overlapping `(bc|b)c` site is enough, while open-ended repeats, conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0242`.
- This task exists so the queue reuses the already-published wider-ranged-repeat grouped backtracking-heavy benchmark anchor instead of pausing after the first grouped-alternation-plus-conditional trio or jumping directly to open-ended grouped-conditionals.
