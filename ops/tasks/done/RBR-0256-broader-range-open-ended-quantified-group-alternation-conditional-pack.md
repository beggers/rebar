# RBR-0256: Publish a broader-range open-ended quantified-group alternation plus conditional correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended grouped-alternation-plus-conditional manifest so the grouped frontier shifts from the landed `{1,}` conditional slice to the `{2,}` lower bound before broader grouped backtracking or deeper grouped execution reopen it.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_conditional_workflows.json`
- `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended grouped-conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){2,})?(?(1)d|e)` and `a(?P<outer>(bc|de){2,})?(?(outer)d|e)` that CPython already accepts.
- The published cases include the absent-group `else` path such as `ae`, lower-bound present-group successes such as `abcbcd` and `adeded`, mixed-branch successes such as `abcded` and `abcbcded`, one bounded fourth-repetition success, plus explicit no-match observations like `abcd` or a haystack whose present-group branch omits the required trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{2,}` envelope around `(bc|de)` wrapped in an optional outer group and followed by one group-exists conditional is enough, while replacement workflows, branch-local backreferences, nested grouped conditionals, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range grouped-alternation-plus-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0255`.
- This task exists so grouped alternation reopens the broader-range open-ended grouped-conditional frontier through one exact `{2,}` slice instead of another vague follow-on bucket.
- Completed 2026-03-13: added a dedicated 14-case broader-range open-ended grouped-alternation-plus-conditional correctness manifest, wired it into the combined harness, regenerated `reports/correctness/latest.json` to 663 total cases across 78 manifests with 649 passes and 14 honest `unimplemented` outcomes, and covered the new suite with a focused conformance test.
