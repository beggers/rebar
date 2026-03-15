# RBR-0372: Publish a nested open-ended quantified-group alternation plus branch-local-backreference callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest so the nested-group callback frontier reopens on correctness publication once `RBR-0370` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbd` or `accd`, one numbered repeated-branch or mixed-haystack path such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the open-ended `{1,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to discover published `*callable_replacement_workflows.py` fixtures and keeps this new manifest explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one open-ended `{1,}` `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacement is enough, while broader lower bounds like `{2,}`, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared callable-parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Queue this behind `RBR-0370` so the broader `{1,4}` callable benchmark catch-up lands before explicit open-ended `{1,}` callback publication reopens correctness work.
- Build on `RBR-0368`, `RBR-0366`, and the existing shared callable-replacement fixture path.
- Keep later parity in the shared callable-replacement pytest surface and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.

## Completion Notes
- Added `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` with the bounded eight-case numbered and named `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` callable-replacement slice for `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d`, reusing only the existing `callable_match_group` helper shape.
- Registered the new manifest in `python/rebar_harness/correctness.py`, threaded it through the combined and open-ended scorecard expectation tables in `tests/conformance/correctness_expectations.py`, and kept the shared callable parity suite honest by marking the new manifest pending in `tests/python/test_callable_replacement_parity_suite.py`, including the compile-metadata skip path for those pending patterns.
- Verified the narrow temporary correctness run with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report /tmp/rbr0372-nested-open-ended-callable-correctness.py`, which reported `8` total cases and `8` honest `unimplemented` cases.
- Republished the tracked correctness scorecard in `reports/correctness/latest.py`; the verified tracked summary is `873` total cases, `865` passed, `0` failed, and `8` unimplemented, and the tracked report now includes the `collection.replacement.nested_open_ended_quantified_group_alternation_branch_local_backreference.callable` suite.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_python_fixture_manifest_contract.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k "combined_correctness_scorecards or open_ended_quantified_group_scorecards"`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
