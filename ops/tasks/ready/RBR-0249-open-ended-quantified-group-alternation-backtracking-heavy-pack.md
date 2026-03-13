# RBR-0249: Publish an open-ended quantified-group alternation backtracking-heavy correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded open-ended grouped backtracking-heavy manifest so the queue reopens overlapping-branch grouped alternation through the already-anchored `{1,}` counted-repeat slice before larger counted ranges or broader grouped-conditionals resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/test_correctness_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated open-ended grouped backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|b)c){1,}d` and `a(?P<word>(bc|b)c){1,}d` that CPython already accepts.
- The published cases include lower-bound successes through both overlapping branches such as `abcd` and `abccd`, repeated and mixed-branch successes such as `abcbcd`, `abcbccd`, `abccbcd`, and one bounded fourth-repetition success, plus explicit no-match observations like `abcccd` or a haystack whose branch choices fail before the trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{1,}` envelope around one overlapping `(bc|b)c` site is enough, while conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, broader counted ranges, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0248`.
- This task exists so the queue reuses the already-published open-ended grouped backtracking-heavy benchmark anchor instead of pausing after the open-ended grouped-conditional trio or jumping to a broader counted-range bucket.
