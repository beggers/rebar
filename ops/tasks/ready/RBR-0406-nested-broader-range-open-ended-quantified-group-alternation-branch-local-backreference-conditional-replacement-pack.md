# RBR-0406: Publish a nested broader-range open-ended quantified-group alternation plus branch-local-backreference conditional replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional replacement manifest so the frontier reopens through one exact replacement-template follow-on after `RBR-0404` closed the adjacent compile/search/fullmatch benchmark gap.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` replacement-template observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){2,})\2(?(2)d|e)` with `\1x` or `\2x`, and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` with `\g<outer>x` or `\g<inner>x`, that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or doubled-haystack path such as `abcbccd`, `abbbdabcbccd`, or `abcbccdaccccd`, one named path that keeps the broader-range `{2,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under template replacement.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one broader-range open-ended `{2,}` nested `(b|c)` site followed immediately by one same-branch backreference and one group-exists conditional feeding replacement templates is enough, and this bounded slice only needs the reachable conditional yes-arm outcomes; callable replacements, broader template parsing, benchmark rows, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended `{2,}` nested-group-alternation-plus-branch-local-backreference conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined correctness helpers and ordinary Python fixture path instead of introducing another frontier-specific harness layer, JSON manifest, or generator.

## Notes
- Build on `RBR-0404`, `RBR-0402`, `RBR-0386`, and the existing open-ended quantified-group replacement publication path.
- Keep later Rust-backed parity on `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` and later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path instead of forking another benchmark family.
