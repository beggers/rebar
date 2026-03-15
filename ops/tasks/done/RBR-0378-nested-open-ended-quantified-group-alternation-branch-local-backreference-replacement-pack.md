# RBR-0378: Publish an open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published correctness scorecard with one bounded open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement manifest so the nested-group replacement frontier reopens on correctness publication once `RBR-0376` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` replacement-template observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){1,})\\2d` with `\\1x` or `\\2x`, and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` with `\\g<outer>x` or `\\g<inner>x`, that CPython already supports.
- The published cases cover at least one numbered lower-bound same-branch path such as `abbd` or `accd`, one numbered repeated-branch or mixed-haystack path such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the open-ended `{1,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable under template replacement.
- The existing combined correctness scorecard suite absorbs this manifest through `tests/conformance/correctness_expectations.py` and `tests/conformance/test_combined_correctness_scorecards.py` instead of growing another bespoke wrapper module.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the published scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one open-ended `{1,}` `(b|c)` site immediately replayed by one same-branch backreference feeding replacement templates is enough, while callable-replacement variants, broader lower bounds like `{2,}`, broader template parsing, broader callback semantics, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixture registration, shared expectation tables, combined-scorecard coverage, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed open-ended `{1,}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement behavior to stdlib `re` outside the existing differential harness path.
- Reuse the existing combined scorecard machinery and ordinary Python fixture path instead of adding JSON manifests, generators, or a manifest-specific harness layer.

## Notes
- Queue this behind `RBR-0376` so the open-ended `{1,}` callable benchmark catch-up lands before replacement-template publication reopens correctness work.
- Build on `RBR-0374` for the exact regex shape and on the existing nested-group replacement publication path already used for `nested_group_replacement_workflows.py` and `quantified_nested_group_replacement_workflows.py`.
- Keep later parity on an ordinary Python pytest path and keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path instead of forking another benchmark family or reviving JSON manifests.

## Completion
- Added `nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows` as an eight-case fixture-backed replacement-template manifest covering numbered and named `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` workflows for `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d`.
- Registered the manifest in `python/rebar_harness/correctness.py` and extended the shared combined/open-ended scorecard expectation tables so the existing combined scorecard regression module picks it up without bespoke harness code.
- Regenerated the tracked combined correctness publication at `reports/correctness/latest.py`; the tracked report now shows `881` total cases across `98` manifests with `873` passes, `0` explicit failures, and `8` honest `unimplemented` outcomes from this new suite.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py` (`9 passed`).
