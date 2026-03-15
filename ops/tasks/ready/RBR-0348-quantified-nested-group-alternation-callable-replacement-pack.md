# RBR-0348: Publish a quantified nested-group alternation callable-replacement correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded quantified nested-group alternation callable-replacement manifest so alternation inside the repeated nested capture becomes the surviving correctness frontier once `RBR-0346` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified nested-group alternation callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d` that CPython already supports.
- The published cases cover at least one numbered lower-bound branch path such as `abd` or `acd`, one numbered repeated or mixed-branch path such as `abccd` or `acbbd`, one named lower-bound or mixed-branch path that keeps the quantified outer capture observable, and one count-limited or first-match-only doubled-haystack case that keeps the final selected inner branch observable under replacement.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one `+`-quantified nested alternation site feeding callable replacement is enough, while broader counted repeats like `{1,4}` or `{1,}`, branch-local-backreference callbacks, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified nested-group alternation callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Build on `RBR-0320`, `RBR-0344`, and the existing callable-replacement fixture path.
- Queue this behind `RBR-0346` so the exact nested-group alternation callback benchmark catch-up lands before quantified callback publication reopens correctness work.
- Keep later parity in the shared callable-replacement pytest surface and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking new task-local harnesses.
