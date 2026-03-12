# RBR-0124: Publish a bounded quantified-alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with one bounded quantified-alternation manifest so the queue combines grouped alternation with bounded repetition before wider alternation-heavy repetition or broader backtracking work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one capturing group whose body contains one literal alternation site repeated across a bounded `{1,2}` range, such as `a(b|c){1,2}d` and `a(?P<word>b|c){1,2}d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the lower-bound and second-repetition outcomes for that exact quantified-alternation shape, including the observable final capture value exposed after the repeated alternation completes.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,2}` quantified alternation site is enough, while wider `{m,n}` envelopes, open-ended repeats, nested alternation inside quantified branches, replacement semantics, branch-local backreferences inside quantified alternation, conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0123`.
- This task exists so the queue reopens alternation-heavy repetition with the smallest exact CPython-supported slice instead of jumping directly to wider repetition or broader backtracking.
