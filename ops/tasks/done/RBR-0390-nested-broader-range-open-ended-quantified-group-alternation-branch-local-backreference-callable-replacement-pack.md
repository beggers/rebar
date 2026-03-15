# RBR-0390: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest so the nested-group callback frontier reopens on correctness publication once `RBR-0388` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or longer-repetition path such as `abcbccd`, `abbbbd`, `accccd`, `abbbdabcbccd`, or `abcbccdabbbd`, one named path that keeps the broader-range open-ended `{2,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to discover published `*callable_replacement_workflows.py` fixtures and keeps this new manifest explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader-range open-ended `{2,}` `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacement is enough, while later Rust-backed callback parity, benchmark catch-up, replacement-template variants, broader callback semantics, broader template parsing, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared callable-parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Queue this behind `RBR-0388` so the broader-range open-ended `{2,}` replacement-template benchmark catch-up lands before the matching callable-replacement publication reopens correctness work.
- Build on `RBR-0374`, `RBR-0376`, `RBR-0386`, and the existing shared callable-replacement fixture path.
- Keep later parity in the shared callable-replacement pytest surface and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.

## Completion
- Added `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` with eight bounded module and compiled-`Pattern` `sub()` / `subn()` callable-replacement cases for `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`, and registered it in `python/rebar_harness/correctness.py`.
- Extended the shared correctness expectation tables so both the combined scorecard suite and the open-ended quantified-group scorecard suite cover the new manifest through the existing generic scorecard runner.
- Updated `tests/python/test_callable_replacement_parity_suite.py` to keep the shared fixture-discovery path explicit for this manifest with an alignment assertion rather than marking it artificially pending.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now records `897` total cases, `897` passed, `0` failed, and `0` unimplemented, and the new callable manifest records `8` passes with `0` gaps.
- The shared callable-replacement parity suite showed these newly published `{2,}` callable cases already pass through the public `rebar` API as a side effect of existing behavior, so queued follow-on `RBR-0392` now appears stale and should be triaged for retirement instead of assumed pending.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py -q`
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -k 'combined_correctness_scorecards or open_ended_quantified_group_scorecards' -q`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
