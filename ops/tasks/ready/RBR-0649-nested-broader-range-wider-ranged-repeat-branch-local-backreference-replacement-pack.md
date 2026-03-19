# RBR-0649: Publish the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template pack

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement-template manifest so the shared replacement frontier reopens on correctness publication once `RBR-0647` drains.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference replacement-template manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded `module.sub()`, `module.subn()`, compiled-`Pattern.sub()`, and compiled-`Pattern.subn()` replacement-template observations through the public `rebar` API for the exact numbered and named workflows:
  - `a((b|c){1,4})\\2d` with `\\1x` or `\\2x`;
  - `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` with `\\g<outer>x` or `\\g<inner>x`.
- The published rows stay pinned to the exact bounded case shape already established by the adjacent wider-ranged-repeat branch-local-backreference and callable-replacement owners:
  - numbered `module.sub(..., "\\1x", "abbd")`, numbered `module.subn(..., "\\2x", "abbbdaccd", 1)`, numbered compiled `Pattern.sub("\\1x", "zzabcbccdzz")`, and numbered compiled `Pattern.subn("\\2x", "zzaccdabcbccdzz", 1)`;
  - named `module.sub(..., "\\g<outer>x", "abcbccd")`, named `module.subn(..., "\\g<inner>x", "abbbdaccd", 1)`, named compiled `Pattern.sub("\\g<outer>x", "zzacccccdzz")`, and named compiled `Pattern.subn("\\g<inner>x", "zzacccccdabbbdzz", 1)`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps the new manifest on the existing shared replacement surface instead of growing another manifest-specific parity module; if live `rebar` still reports placeholder behavior for this new `{1,4}` slice, keep the manifest explicit as the shared follow-on rather than silently dropping it from parity coverage.
- `tests/conformance/correctness_expectations.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1310` total / `1310` passed / `0` `unimplemented` across `110` manifests to `1318` total across `111` manifests; and
  - the new manifest publishes `8` total cases with `str` text-model coverage and reports them honestly as `pass` or `unimplemented` according to the live `rebar` result.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py --report .rebar/tmp/rbr-0649-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement new replacement behavior just to make the new cases pass.
- Do not broaden into bytes, callable replacement, open-ended `{1,}` or broader-range open-ended `{2,}` replacement-template rows, benchmark rows, broader template parsing, or another branch-local-backreference family in this run.
- Keep later Rust-backed parity on the shared `tests/python/test_fixture_backed_replacement_parity_suite.py` surface and later Python-path benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path instead of forking another fixture owner or benchmark family.

## Notes
- `RBR-0649` is the next available feature task id in the current checkout; `RBR-0648` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0647` so the broader `{2,}` replacement bytes benchmark catch-up lands before the missing broader `{1,4}` nested replacement-template slice reopens correctness work on the ordinary shared replacement path.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py` already pins the exact `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` broader `{1,4}` numbered and named branch-local-backreference frontier, including the lower-bound, mixed-branch, upper-bound, and first-match-only observation texts this replacement-template pack should mirror;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py` already carries the matching eight module and compiled-`Pattern` replacement owner shapes for this same `{1,4}` slice, so the template pack can stay on the same bounded operation and haystack shape without another synthesis pass;
  - `python/rebar_harness/correctness.py` currently publishes the wider-ranged-repeat nested branch-local-backreference and callable-replacement manifests but no matching `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` fixture yet;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` and `tests/benchmarks/benchmark_expectations.py` currently contain the `{1,}`, `{2,}`, and `{2,}` conditional nested branch-local-backreference replacement-template rows but no adjacent `{1,4}` wider-ranged-repeat replacement rows, so a later benchmark catch-up can stay on the existing shared replacement manifest once correctness publication and parity land; and
  - no tracked task, published fixture, or shared replacement benchmark slice currently covers the `{1,4}` nested branch-local-backreference replacement-template sibling between the already-landed plain branch-local-backreference and callable-replacement fronts, so this pack is the smallest explicit missing slice on that owner path.
