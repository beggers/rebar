# RBR-0354: Publish a nested-group alternation plus branch-local-backreference callable-replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine nested-group alternation, same-branch backreferences, and callable replacement so branch-local-backreference callbacks become the surviving correctness frontier after `RBR-0352` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group-alternation-plus-branch-local-backreference callable-replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` callable-replacement observations through the public `rebar` API for the exact numbered and named workflows `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` that CPython already supports.
- The published cases cover at least one numbered same-branch callback success such as `abbd` or `accd`, one numbered first-match-only mixed-haystack case such as `abbdaccd` or `accdabbd` that keeps the selected inner branch observable under replacement, one named outer-capture case that keeps both named captures distinguishable under a successful same-branch backreference, and one named first-match-only case on a doubled or mixed haystack.
- The callable replacements stay bounded to the existing `callable_match_group` helper shape by reading `match.group(1)` or `match.group(2)` for numbered workflows and `match.group("outer")` or `match.group("inner")` for named workflows; the task does not broaden into arbitrary callback behavior.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture containing one inner alternation immediately replayed by one same-branch backreference feeding callable replacement is enough, while quantified branch-local-backreference callbacks, broader counted repeats like `{1,4}` or `{1,}`, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group-alternation-plus-branch-local-backreference callable-replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing `callable_match_group` helper and combined scorecard machinery instead of adding a manifest-specific harness layer.

## Notes
- Queue this immediately behind `RBR-0352` so the quantified nested-group alternation callable-replacement benchmark catch-up lands before branch-local-backreference callback publication reopens correctness work.
- Build on `RBR-0326`, `RBR-0344`, and the existing callable-replacement fixture path.
- Keep later parity in the shared callable-replacement pytest surface and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.

## Completion Notes
- Added `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py` and wired it into `python/rebar_harness/correctness.py`, publishing eight bounded numbered and named `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` callable-replacement observations for `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d`.
- Extended `tests/conformance/correctness_expectations.py` so the existing combined scorecard suite asserts the new manifest without adding another bespoke scorecard wrapper.
- Updated the shared callable parity suite in `tests/python/test_callable_replacement_parity_suite.py` so the new manifest shape is covered immediately while rebar-backed execution for this one pending callable slice stays explicitly skipped until `RBR-0356` lands.
- Republished `reports/correctness/latest.py`; the tracked combined correctness scorecard now reports `849` total cases across `94` manifests with `841` passes, `0` explicit failures, and `8` honest `unimplemented` outcomes, all in the new `collection.replacement.nested_group_alternation_branch_local_backreference.callable` suite.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report /tmp/rebar-rbr0354-narrow-correctness.json`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/python/test_callable_replacement_parity_suite.py`.
