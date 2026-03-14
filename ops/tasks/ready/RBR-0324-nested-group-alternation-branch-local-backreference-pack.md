# RBR-0324: Publish a bounded nested-group-alternation-plus-branch-local-backreference correctness pack

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine nested-group alternation with a same-branch backreference so the remaining explicit gap on the existing nested-group alternation benchmark anchor becomes the surviving frontier after `RBR-0322`.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_workflows.py`
- `tests/conformance/test_correctness_nested_group_alternation_branch_local_backreference_workflows.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include explicit present-branch successes like `abbd` and `accd`, a no-match observation like `abd` or `acd`, and one named-path case that keeps both the outer and inner captures observable under a successful same-branch backreference.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture containing one inner alternation followed by one same-branch backreference is enough, while quantified nested alternation plus backreferences, broader counted repeats, replacement semantics, conditionals, and deeper nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.py`.

## Notes
- Queue this immediately behind `RBR-0322` so the current quantified nested-group alternation benchmark catch-up lands before the remaining explicit nested-group alternation gap reopens as correctness work.
- Build on `RBR-0087`, `RBR-0090`, and `RBR-0322`.
- Keep later parity and benchmark follow-ons on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path, which already carries the named branch-local-backreference gap anchor instead of forking another benchmark family.
