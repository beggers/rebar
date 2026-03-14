# RBR-0342: Publish a nested-group alternation callable-replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded nested-group alternation callable-replacement manifest so branch selection inside a nested capture becomes the next explicit correctness frontier once the current broader `{1,4}` benchmark-catch-up head drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group alternation callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d` that CPython already supports.
- The published cases cover at least one numbered `b`-branch callback path such as `abd`, one numbered mixed-haystack path such as `abdacd` or `acdabd`, one named `c`-branch callback path, and one count-limited or first-match-only case so the outer capture plus final inner branch stay observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested alternation site feeding callable replacement is enough, while quantified nested alternation callbacks, branch-local-backreference callbacks, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group alternation callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Build on the existing grouped-alternation callable-replacement, nested-group callable-replacement, and nested-group alternation surfaces already published in the repo.
- Keep later parity and benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path, which already carries the `module-sub-callable-nested-group-alternation-cold-gap` anchor; do not fork another benchmark family for this bounded slice.
