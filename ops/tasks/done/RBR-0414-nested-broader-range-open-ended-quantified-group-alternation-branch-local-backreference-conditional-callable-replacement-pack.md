# RBR-0414: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference conditional callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional callable-replacement manifest so the frontier reopens on correctness publication once `RBR-0410` has closed the adjacent replacement-template benchmark gap.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or doubled-haystack path such as `abcbccd`, `abbbdabcbccd`, or `abcbccdaccccd`, one named path that keeps the broader-range open-ended `{2,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to discover published `*callable_replacement_workflows.py` fixtures and keeps this new manifest explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one broader-range open-ended `{2,}` nested `(b|c)` site followed immediately by one same-branch backreference and one group-exists conditional feeding callable replacement is enough, and this bounded slice only needs the reachable conditional yes-arm outcomes; replacement templates, broader callback semantics, benchmark rows, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared callable-parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and shared callable parity surface instead of adding another manifest-specific harness layer.

## Notes
- Build on `RBR-0410`, `RBR-0408`, `RBR-0395`, and the existing shared callable-replacement fixture path.
- Keep later Rust-backed parity on `tests/python/test_callable_replacement_parity_suite.py` and later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.

## Completion
- Added the new conditional callable-replacement fixture pack, registered it in `python/rebar_harness/correctness.py`, and extended the shared correctness expectations so the combined and open-ended scorecard suites publish the new manifest.
- Updated `tests/python/test_callable_replacement_parity_suite.py` so the shared callable parity surface discovers the new fixture and keeps it explicitly pending for `rebar` until `RBR-0415`.
- Republished the tracked combined correctness scorecard in `reports/correctness/latest.py`; the tracked artifact now reports 933 total cases, 925 passing cases, 0 explicit failures, and 8 unimplemented cases.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/python/test_callable_replacement_parity_suite.py` and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
