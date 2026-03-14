# RBR-0297: Publish a nested broader-range wider-ranged-repeat quantified-group alternation backtracking-heavy correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded nested broader `{1,4}` grouped backtracking-heavy manifest so the frontier reopens one exact nested overlapping-branch composition immediately after `RBR-0295` closes benchmark catch-up for the adjacent nested grouped-conditional slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested broader-range wider-ranged-repeat grouped backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d` that CPython already accepts.
- The published cases include lower-bound successes through both overlapping branches such as `abcd` and `abccd`, mixed second-repetition successes such as `abcbccd` and `abccbcd`, one upper-bound four-repetition success such as `abcbccbccbcd`, plus explicit no-match observations like `abccbd` or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader `{1,4}` overlapping `(bc|b)c` site is enough, while grouped replacement workflows, conditional compositions, branch-local backreferences, and broader nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested broader-range grouped backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0295`.
- Keep the later parity and benchmark follow-ons on the existing `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` and `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` paths; do not fork a new parity module or benchmark family when those tasks are seeded.

## Completion Note
- Added the new nested broader `{1,4}` grouped backtracking-heavy fixture and default-harness wiring for `a(((bc|b)c){1,4})d` plus `a(?P<outer>((bc|b)c){1,4})d`, along with a dedicated conformance test and widened wider-ranged-repeat scorecard expectations for the new manifest.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 85 manifests, 771 total cases, 757 passes, and 14 honest `unimplemented` cases from this new publication pack.
- Verified with `python3 -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows`, `python3 -m unittest tests.conformance.test_wider_ranged_repeat_quantified_group_scorecards`, `python3 -m unittest tests.conformance.test_combined_correctness_scorecards`, and `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
