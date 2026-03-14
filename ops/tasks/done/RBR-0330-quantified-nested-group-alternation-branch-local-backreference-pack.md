# RBR-0330: Publish a quantified nested-group-alternation-plus-branch-local-backreference correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded quantified nested-group-alternation-plus-branch-local-backreference manifest so the next quantified nested-backreference frontier is explicit after `RBR-0328` closes the remaining benchmark gap on `nested_group_alternation_boundary.py`.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_workflows.py`
- `tests/conformance/test_correctness_quantified_nested_group_alternation_branch_local_backreference_workflows.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified nested-group-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded compile, module-search, and compiled-`Pattern.fullmatch()` observations through the public `rebar` API for the exact numbered and named workflows `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d` that CPython already supports.
- The published cases include lower-bound single-branch successes like `abbd` and `accd`, repeated-branch successes like `abbbd`, `abccd`, or `acbbd`, one explicit no-match observation like `abcd` or `acbd`, and one named-path case that keeps the quantified outer capture plus final inner branch observable under repetition.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture containing one `+`-quantified inner numbered or named alternation site immediately replayed by one same-branch backreference is enough, while broader counted repeats like `{1,4}` or `{1,}`, replacement semantics, conditionals, whole-pair counted envelopes, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified nested-group-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.py`.

## Notes
- Queue this immediately behind `RBR-0328` so benchmark catch-up for the non-quantified slice lands before the next correctness frontier reopens.
- Build on `RBR-0320`, `RBR-0326`, and the current `RBR-0328` benchmark catch-up.
- Keep later parity and benchmark follow-ons on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path instead of forking another benchmark family for the same bounded nested-group alternation frontier.

## Completion Notes
- Added a dedicated ten-case manifest for `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`, covering numbered and named compile metadata, lower-bound `search()` / `Pattern.fullmatch()` successes, repeated-branch successes, and explicit no-match paths without widening runtime scope.
- Registered the new manifest in `python/rebar_harness/correctness.py`, added a dedicated correctness scorecard test, and updated the shared combined-scorecard expectations so the new manifest is part of the tracked correctness inventory.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now reports 811 total cases, 801 passes, 0 failures, and 10 honest `unimplemented` outcomes across 90 manifests, with the new quantified nested-group alternation plus branch-local backreference suite contributing 10 `unimplemented` cases.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_workflows.py --report /tmp/rbr0330_fixture_report.json`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_correctness_quantified_nested_group_alternation_branch_local_backreference_workflows.py -q`.
