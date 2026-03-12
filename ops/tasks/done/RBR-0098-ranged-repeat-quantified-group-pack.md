# RBR-0098: Publish a bounded ranged-repeat quantified-group correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded ranged-repeat quantified-group manifest so quantified execution broadens from exact counts into the smallest bounded range before quantified alternation, conditionals, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/ranged_repeat_quantified_group_workflows.json`
- `tests/conformance/test_correctness_ranged_repeat_quantified_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated ranged-repeat quantified-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one bounded `{1,2}` numbered or named capturing group inside literal prefix/suffix text, such as `a(bc){1,2}d` and `a(?P<word>bc){1,2}d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover both lower-bound and upper-bound outcomes for that exact bounded-range capture shape, including the observable match-object group values exposed after the ranged repetition completes.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,2}` capture site is enough, while open-ended repeats, wider `{m,n}` ranges, quantified alternation, replacement semantics, conditionals, nested quantified groups, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed ranged-repeat quantified-group behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0096` and `RBR-0097`.
- This task exists so the worker can continue quantified execution from exact counts into one bounded ranged-repeat slice instead of jumping directly to quantified alternation, conditionals, or broader backtracking.

## Completion
- Added `ranged-repeat-quantified-group-workflows` to the default correctness manifest set with six bounded `{1,2}` numbered and named capture cases covering compile metadata plus lower-bound and upper-bound module/`Pattern` observations.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports 182 total cases with 176 passes, 0 explicit failures, and 6 honest `unimplemented` ranged-repeat gaps.
