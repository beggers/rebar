# RBR-0366: Publish a nested broader-range wider-ranged-repeat quantified-group alternation plus branch-local-backreference callable-replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest so the frontier reopens on the existing nested-group callback anchor once `RBR-0364` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbd` or `accd`, one numbered broader counted-repeat or mixed-branch path such as `abbbd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the broader `{1,4}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to discover published `*callable_replacement_workflows.py` fixtures and keeps this new manifest explicitly pending until later parity lands; do not add another manifest-specific callable-replacement parity module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one broader `{1,4}` `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacement is enough, while open-ended counted repeats, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, shared callable-parity fixture bookkeeping, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Build on `RBR-0362`, `RBR-0338`, and the queued `RBR-0364`.
- Queue this behind `RBR-0364` so the quantified callable benchmark catch-up lands before broader `{1,4}` callable publication reopens correctness work.
- Keep later parity in the shared callable-replacement pytest surface and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
