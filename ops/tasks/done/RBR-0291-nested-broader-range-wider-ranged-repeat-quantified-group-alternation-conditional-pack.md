# RBR-0291: Publish a nested broader-range wider-ranged-repeat quantified-group alternation plus conditional correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded nested broader `{1,4}` grouped-alternation-plus-conditional manifest so the frontier reopens deeper grouped conditional composition immediately after `RBR-0289` catches the adjacent nested broader grouped-alternation slice up on the Python-path benchmark surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested broader-range wider-ranged-repeat grouped-alternation-plus-conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)` that CPython already accepts.
- The published cases include the absent-group `else` path on `af`, lower-bound present-group successes such as `abcde` and `adede`, mixed and upper-bound present-group successes such as `abcbcdede` and `adedededede`, plus explicit no-match observations like `ae`, a present-group branch that omits the final conditional `e`, or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope before the later conditional can match.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one optional outer capture around the already-landed nested broader grouped-alternation subpattern plus one later group-exists conditional is enough, while nested grouped backtracking-heavy follow-ons, replacement workflows, branch-local backreferences, and broader nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested broader grouped-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on the Rust-backed behavior already landed in `RBR-0287`, but keep this publication task queued after `RBR-0289` so benchmark catch-up closes the current nested grouped-alternation slice before deeper grouped follow-ons reopen the frontier.
- Keep the later parity and benchmark follow-ons on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path; do not fork a new benchmark family when those tasks are seeded.

## Completion Note
- Added `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`, registered it in `python/rebar_harness/correctness.py`, and extended `tests/conformance/correctness_expectations.py` so the existing wider-ranged-repeat scorecard suite now covers the new nested grouped-conditional manifest.
- Published 14 new numbered and named compile/module/pattern cases for `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)`, covering the absent `af` else path, lower-bound `abcde` and `adede`, mixed `abcbcdede`, upper-bound `adedededede`, plus explicit no-match observations for `ae`, a missing conditional `e`, and a fifth grouped repetition overflow.
- Regenerated `reports/correctness/latest.json`; the combined correctness scorecard now reports 84 manifests, 757 total cases, 743 passes, 14 honest `unimplemented` outcomes, and 0 explicit failures. The new manifest reports 14 total cases with 14 `unimplemented` results.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python python3 -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp-rbr-0291-single.json`, `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`, and `PYTHONPATH=python python3 -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows tests.conformance.test_wider_ranged_repeat_quantified_group_scorecards tests.conformance.test_combined_correctness_scorecards`.
