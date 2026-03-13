# RBR-0198: Publish a bounded nested two-arm conditional replacement correctness pack

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published correctness scorecard with a bounded nested two-arm conditional replacement manifest so replacement-conditioned work reopens through one explicit nested follow-on instead of a vague broader-composition bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_nested_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_nested_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested two-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows using constant replacement text on `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` through module and compiled-`Pattern` `sub()` and `subn()` entrypoints that CPython already supports.
- The published cases cover both capture-present and capture-absent outcomes for that exact nested replacement shape, including the bounded present workflow where the outer and inner yes arms require `d` before replacement text is emitted and the absent workflow where the outer else arm contributes `f`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer two-arm conditional whose yes arm contains one nested two-arm conditional site is enough, while replacement templates that read capture groups, callable replacement semantics, alternation-heavy nested arms, quantified repeats, deeper nesting, branch-local backreferences, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0183`, `RBR-0194`, and the existing conditional replacement helper surface.
- This task exists so the queue reopens after `RBR-0197` with the smallest remaining nested replacement-conditioned gap instead of jumping directly to quantified replacement-conditioned conditionals, branch-local-backreference arms, or a vague broader-backtracking bucket.
- Added `conditional_group_exists_nested_replacement_workflows.json`, registered it in the default combined harness fixture list, and published the new eight-case nested replacement suite in `reports/correctness/latest.json`.
- Current runtime behavior remains honest-gap publication for this slice: the combined scorecard now reports 440 total cases with 8 `unimplemented` nested replacement cases, and `python3 -m unittest discover -s tests/conformance -p 'test_correctness_conditional_group_exists*.py'` passed after the baseline update.
