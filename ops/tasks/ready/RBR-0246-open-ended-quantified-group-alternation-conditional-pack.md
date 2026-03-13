# RBR-0246: Publish an open-ended quantified-group alternation plus conditional correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded open-ended grouped-alternation-plus-conditional manifest so the queue reopens conditional composition through the already-anchored `{1,}` counted-repeat slice before broader grouped backtracking resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.json`
- `tests/conformance/test_correctness_open_ended_quantified_group_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){1,})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,})?(?(outer)d|e)` that CPython already accepts.
- The published cases include the absent-group `else` path such as `ae`, lower-bound present-group successes such as `abcd` and `aded`, repeated and mixed-branch successes such as `abcded`, `abcbcded`, and `adededed`, plus explicit no-match observations like `ad` or a haystack whose present-group branch omits the required trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{1,}` envelope around `(bc|de)` wrapped in an optional outer group and followed by one group-exists conditional is enough, while replacement workflows, branch-local backreferences, nested grouped conditionals, broader counted ranges, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed grouped-alternation-plus-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0245`.
- This task exists so grouped alternation reopens the already-anchored open-ended grouped-conditional frontier through one exact `{1,}` slice instead of another vague follow-on bucket.
