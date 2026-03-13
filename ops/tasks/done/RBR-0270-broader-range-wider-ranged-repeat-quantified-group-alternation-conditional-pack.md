# RBR-0270: Publish a broader-range wider ranged-repeat quantified-group alternation plus conditional correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published correctness scorecard with one broader `{1,4}` grouped-alternation-plus-conditional manifest so the frontier reopens conditional composition through the newly benchmark-caught-up counted-repeat envelope instead of jumping to a looser backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.json`
- `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)` that CPython already accepts.
- The published cases include the absent-group `else` path such as `ae`, lower-bound present-group successes such as `abcd` and `aded`, mixed and upper-bound present-group successes such as `abcbcded` and `abcdededed`, plus explicit no-match observations like `ad`, a present-group branch that omits the required trailing `d`, or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one broader `{1,4}` grouped-alternation site plus one group-exists conditional is enough, while open-ended repeats, replacement workflows, branch-local backreferences, nested grouped conditionals, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation-plus-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0269`.
- Keep the eventual parity and benchmark follow-ons on the existing wider-ranged-repeat grouped boundary path; do not fork a new benchmark family for this broader `{1,4}` conditional slice.

## Completion
- Added `broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows` to the default correctness manifest set with 14 numbered and named compile/module/pattern observations covering the absent `ae` else-arm path, lower-bound hits on `abcd` and `aded`, broader present-group hits on `abcbcded` and `abcdededed`, plus explicit `ad`, missing-trailing-`d`, and fifth-repetition overflow no-match cases.
- Added `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py` to pin the combined-scorecard suite ids, family list, and CPython-visible observations for the new broader `{1,4}` grouped-conditional pack.
- Republished `reports/correctness/latest.json`; the combined correctness scorecard now covers 82 manifests / 715 cases, with this new broader `{1,4}` grouped-alternation-plus-conditional slice remaining explicit as 14 honest `unimplemented` cases and no explicit failures.
