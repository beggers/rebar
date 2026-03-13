# RBR-0240: Publish a bounded wider ranged-repeat quantified-group alternation plus conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded grouped-alternation-plus-conditional manifest so the queue reopens conditional composition through an already-anchored `{1,3}` counted-repeat slice before broader grouped backtracking or open-ended grouped-conditionals resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_conditional_workflows.json`
- `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){1,3})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,3})?(?(outer)d|e)` that CPython already accepts.
- The published cases include the absent-group `else` path such as `ae`, lower-bound present-group successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcded` and `abcbcded`, plus explicit no-match observations like `ad` or a haystack whose present-group branch lacks the required trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,3}` grouped-alternation site plus one group-exists conditional is enough, while open-ended repeats, replacement workflows, branch-local backreferences, nested grouped conditionals, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation-plus-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0239`.
- This task exists so grouped alternation reopens conditional composition through one exact bounded `{1,3}` slice instead of a vague broader backtracking bucket.
