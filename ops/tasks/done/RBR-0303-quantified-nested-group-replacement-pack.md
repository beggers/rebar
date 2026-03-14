# RBR-0303: Publish a quantified nested-group replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded quantified nested-group replacement manifest so grouped replacement work reopens immediately after `RBR-0301` catches the adjacent nested broader `{1,4}` grouped backtracking-heavy match slice up on the benchmark surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py`
- `tests/conformance/test_correctness_quantified_nested_group_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified nested-group replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for quantified nested captures on `a((bc)+)d` with `\\1x` or `\\2x`, and `a(?P<outer>(?P<inner>bc)+)d` with `\\g<outer>x` or `\\g<inner>x`, through module and compiled-`Pattern` `sub()` and `subn()` entrypoints that CPython already supports.
- The published cases cover at least one lower-bound one-repetition replacement path such as `abcd`, one repeated-inner-capture path such as `abcbcd`, and one count-limited path such as replacing only the first match in `abcbcdabcbcd`, so the outer capture and final inner capture values stay observable under repetition.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one quantified inner nested capture feeding numbered or named replacement templates is enough, while callable replacement semantics, alternation inside the repeated site, broader counted-repeat shapes like `{1,4}` or open-ended grouped backtracking, branch-local backreferences, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified nested-group replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0301`.
- Keep later parity and benchmark follow-ons on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path, which already exposes the quantified nested-group replacement gap row; do not fork another benchmark family when those follow-ons are seeded.
- Add only the directly adjacent numbered and named template cases needed to make this exact repeated-inner-capture slice visible; quantified callable replacement and broader nested grouped replacement follow-ons stay out of scope.

## Completion Notes
- Added `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py` with eight bounded numbered and named `sub()`/`subn()` cases covering the lower-bound `abcd`, repeated `abcbcd`, and first-match-only `abcbcdabcbcd` template-replacement paths for `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d`.
- Wired the new manifest into `python/rebar_harness/correctness.py`, added combined-scorecard representative cases in `tests/conformance/correctness_expectations.py`, and added `tests/conformance/test_correctness_quantified_nested_group_replacement_workflows.py` to assert the new suite is published as eight honest `unimplemented` gaps with the expected CPython results.
- Regenerated `reports/correctness/latest.json`; the combined scorecard now reports 779 total cases, 771 passes, 0 explicit failures, and 8 unimplemented cases.
- Verified with `PYTHONPATH=python python3 -m unittest tests.conformance.test_correctness_fixture_inventory_contract tests.conformance.test_correctness_quantified_nested_group_replacement_workflows tests.conformance.test_combined_correctness_scorecards`.
