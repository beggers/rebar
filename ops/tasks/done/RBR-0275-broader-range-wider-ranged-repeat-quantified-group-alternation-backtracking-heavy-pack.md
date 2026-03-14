# RBR-0275: Publish a broader-range wider ranged-repeat quantified-group alternation backtracking-heavy correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` grouped backtracking-heavy manifest so the frontier widens the overlapping-branch wider-ranged-repeat slice immediately after `RBR-0273` catches the adjacent grouped-conditional slice up on the Python-path benchmark surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range wider-ranged-repeat grouped backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|b)c){1,4}d` and `a(?P<word>(bc|b)c){1,4}d` that CPython already accepts.
- The published cases include lower-bound successes through both overlapping branches such as `abcd` and `abccd`, mixed-branch and upper-bound successes such as `abcbccd`, `abccbcd`, and one bounded fourth-repetition success, plus explicit no-match observations like `abccbd` or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,4}` envelope around one overlapping `(bc|b)c` site is enough, while open-ended repeats, grouped conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range grouped backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0273`.
- Keep the eventual parity and benchmark follow-ons on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path; do not fork another benchmark family when this broader `{1,4}` grouped backtracking-heavy slice is later caught up on the Python-path benchmark surface.

## Completion
- Added the new broader `{1,4}` grouped backtracking-heavy fixture and default-harness wiring for `a((bc|b)c){1,4}d` plus `a(?P<word>(bc|b)c){1,4}d`.
- Added a focused conformance test and republished `reports/correctness/latest.json`; the combined scorecard now reports 83 manifests, 729 total cases, 715 passes, and 14 honest `unimplemented` cases from this new publication pack.
- Verified with `python3 -m unittest tests.conformance.test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows`.
