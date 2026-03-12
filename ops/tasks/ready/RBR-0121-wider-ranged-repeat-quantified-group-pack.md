# RBR-0121: Publish a bounded wider ranged-repeat quantified-group correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with one wider ranged-repeat quantified-group manifest so counted execution broadens one notch beyond the landed `{1,2}` slice before quantified alternation or broader backtracking work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_workflows.json`
- `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated wider ranged-repeat quantified-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one numbered or named capturing group repeated across a slightly wider `{1,3}` range inside literal prefix/suffix text, such as `a(bc){1,3}d` and `a(?P<word>bc){1,3}d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the lower bound and the new third-repetition upper-bound outcome for that exact `{1,3}` shape, including the observable match-object group values exposed after the wider repetition completes.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one wider `{1,3}` capture site is enough, while open-ended repeats, still-wider `{m,n}` envelopes, quantified alternation inside repeated groups, replacement semantics, conditionals, nested quantified groups, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed wider ranged-repeat behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0120`.
- This task exists so the queue reopens counted execution with one slightly wider exact CPython-supported range before it jumps to quantified alternation or broader backtracking.
