# RBR-0384: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement manifest so the nested-group replacement frontier reopens on correctness publication once `RBR-0382` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` replacement-template observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\\2d` with `\\1x` or `\\2x`, and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` with `\\g<outer>x` or `\\g<inner>x`, that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or longer-repetition path such as `abcbccd`, `abbbbd`, `accccd`, `abbbdabcbccd`, or `abcbccdabbbd`, one named path that keeps the shifted `{2,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under template replacement.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader-range open-ended `{2,}` `(b|c)` site immediately replayed by one same-branch backreference feeding replacement templates is enough, while Rust-backed parity, benchmark catch-up, callable-replacement variants, broader template parsing, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined scorecard machinery and ordinary Python fixture path instead of adding JSON manifests, generators, or a manifest-specific harness layer.

## Notes
- Queue this behind `RBR-0382` so the open-ended `{1,}` benchmark catch-up lands before broader-range open-ended `{2,}` replacement-template publication reopens correctness work.
- Build on `RBR-0378`, `RBR-0380`, and the existing nested-group replacement publication path already used for the adjacent `{1,}` replacement-template slice.
- Keep later parity on an ordinary Python pytest path and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path instead of forking another benchmark family or reviving JSON manifests.

## Completion Note
- Added `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` with 8 bounded `sub()`/`subn()` module and compiled-`Pattern` template-replacement cases for `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`.
- Registered the fixture in `python/rebar_harness/correctness.py` and extended the shared combined/open-ended scorecard expectation tables in `tests/conformance/correctness_expectations.py`, so the existing scorecard tests absorb the new manifest without a bespoke wrapper.
- Scratch correctness run for the new manifest published 8 executed cases with 8 honest `unimplemented` outcomes.
- Republished `reports/correctness/latest.py`; the tracked report now shows 889 total cases, 881 passes, 0 failures, 8 `unimplemented`, and 99 manifests.
- Verified with `./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardSuitesTest::test_runner_regenerates_combined_correctness_scorecards tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardSuitesTest::test_runner_regenerates_open_ended_quantified_group_scorecards` (`2 passed`, `435 subtests passed`).
