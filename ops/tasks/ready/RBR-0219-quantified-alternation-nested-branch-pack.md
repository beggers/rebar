# RBR-0219: Publish a bounded quantified-alternation nested-branch correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a `{1,2}` quantified outer alternation with one nested alternation branch so quantified alternation keeps widening through an exact nested-branch follow-on before wider counted ranges, open-ended repeats, or broader backtracking resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_nested_branch_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-alternation nested-branch manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b|c)|de){1,2}d` and `a(?P<word>(b|c)|de){1,2}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes through both the inner `b|c` branch and the sibling `de` branch, second-repetition successes that mix those branch selections across the `{1,2}` envelope, plus explicit no-match observations that show the trailing literal `d` still sits outside the quantified group.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,2}` outer capture whose alternation chooses either one nested `b|c` site or one literal `de` branch is enough, while wider counted ranges, open-ended repeats, branch-local backreferences, conditionals, replacement semantics, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-alternation nested-branch behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0125`, `RBR-0126`, and `RBR-0218`.
- This task exists so the queue keeps widening quantified alternation through one exact nested-branch follow-on with an existing benchmark anchor instead of jumping directly to wider counted ranges, open-ended repeats, or vague broader backtracking.
