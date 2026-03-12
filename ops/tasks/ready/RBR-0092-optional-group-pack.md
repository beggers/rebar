# RBR-0092: Publish a bounded optional-group correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded optional-group manifest so quantified execution reopens through the smallest capture-aware slice before counted repeats, quantified alternation, conditionals, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/optional_group_workflows.json`
- `tests/conformance/test_correctness_optional_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated optional-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one optional numbered or named capturing group inside literal prefix/suffix text, such as `a(b)?d` and `a(?P<word>b)?d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover both the group-present and group-omitted outcomes for that exact `?`-quantified capture shape, including the observable match-object group values that differ when the optional capture is absent.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one optional capture site is enough, while `*`/`+`/`{m,n}` repeats, quantified alternation, replacement semantics, conditionals, nested quantified groups, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed optional-group behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0050`, `RBR-0078`, and `RBR-0091`.
- This task exists so the worker can reopen quantified execution with a bounded capture-aware slice instead of jumping directly to counted repeats, quantified alternation, or conditionals.
