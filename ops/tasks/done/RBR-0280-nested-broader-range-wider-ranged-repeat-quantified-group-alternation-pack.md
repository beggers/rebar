# RBR-0280: Publish a nested broader-range wider-ranged-repeat quantified-group alternation correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded nested broader `{1,4}` grouped-alternation manifest so the frontier reopens deeper grouped execution immediately after `RBR-0278` finishes benchmark catch-up for the adjacent top-level `{1,4}` slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested broader-range wider-ranged-repeat quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d` that CPython already accepts.
- The published cases include lower-bound successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcbcded` and `adedededed`, plus explicit no-match observations like `ae`, a haystack whose grouped body omits the required trailing `d`, or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader `{1,4}` `(bc|de)` site is enough, while nested grouped conditionals, nested grouped backtracking-heavy follow-ons, replacement workflows, and broader nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested broader-range grouped-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0278`.
- Keep the later benchmark catch-up for this slice on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path; do not fork a new benchmark family when follow-on parity and benchmark tasks are seeded.

## Completion Notes
- Added the nested broader `{1,4}` grouped-alternation pack as `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py` and inserted it into `DEFAULT_FIXTURE_PATHS` immediately after the adjacent top-level broader `{1,4}` grouped-alternation manifest so the published combined scorecard reopens deeper grouped execution without changing the existing path-based harness contract.
- Published 14 new numbered and named compile/module/pattern cases for `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d`, covering lower-bound `abcd` and `aded`, mixed `abcbcded`, upper-bound `adedededed`, plus explicit no-match observations for `ae`, a missing trailing `d`, and a fifth repetition overflow.
- Regenerated `reports/correctness/latest.json`; the combined correctness scorecard now reports 83 manifests, 743 total cases, 729 passes, 14 honest `unimplemented` outcomes, and 0 explicit failures.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py --report /tmp/rbr0280-correctness.json`, `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`, and `PYTHONPATH=python python3 -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows tests.conformance.test_wider_ranged_repeat_quantified_group_scorecards tests.conformance.test_combined_correctness_scorecards`.
