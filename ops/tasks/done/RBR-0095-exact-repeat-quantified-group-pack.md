# RBR-0095: Publish a bounded exact-repeat quantified-group correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded exact-repeat quantified-group manifest so quantified execution continues through the smallest deterministic counted slice before ranged repeats, quantified alternation, conditionals, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/exact_repeat_quantified_group_workflows.json`
- `tests/conformance/test_correctness_exact_repeat_quantified_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated exact-repeat quantified-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one exact `{2}` numbered or named capturing group inside literal prefix/suffix text, such as `a(bc){2}d` and `a(?P<word>bc){2}d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the observable match-object group values exposed after the exact-count repetition completes, without broadening into capture-history semantics beyond what CPython already exposes through `group()` and `groups()`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact `{2}` capture site is enough, while `{m,n}` ranges, `?`/`*`/`+` repeats beyond the already-published optional-group slice, quantified alternation, replacement semantics, conditionals, nested quantified groups, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed exact-repeat quantified-group behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0050`, `RBR-0078`, and `RBR-0093`.
- This task exists so the worker can continue quantified execution with one deterministic counted slice instead of jumping directly to ranged repeats, quantified alternation, or conditionals.

## Completion
- Completed 2026-03-12.
- Added `exact-repeat-quantified-group-workflows` to the combined correctness fixture set with six bounded `{2}` numbered/named group cases across compile, module `search()`, and bound `Pattern.fullmatch()` paths.
- Regenerated `reports/correctness/latest.json`; the published scorecard now reports `176` total cases with `170` passes and `6` honest `unimplemented` outcomes for the new exact-repeat slice.
