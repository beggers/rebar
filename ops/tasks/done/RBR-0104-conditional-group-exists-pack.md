# RBR-0104: Publish a bounded conditional group-exists correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded conditional manifest so the queue reopens conditional execution through the smallest capture-aware slice before assertion-conditioned branches or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows where an already-open optional numbered or named capture controls a conditional branch, such as `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover both the group-present and group-omitted outcomes for that exact group-exists conditional shape, including the observable match-object group values that differ when the optional capture is absent.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one conditional site keyed by an already-open group is enough, while assertion-tested conditionals, nested conditionals, conditional replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0093`, `RBR-0102`, and `RBR-0103`.
- This task exists so the worker can reopen conditional execution with the smallest capture-aware slice instead of jumping directly to assertion-conditioned branches or broader backtracking semantics.

## Completion Notes
- Added `tests/conformance/fixtures/conditional_group_exists_workflows.json` with six bounded numbered and named group-exists conditional cases covering compile metadata plus present/absent public workflow observations.
- Wired the manifest into `python/rebar_harness/correctness.py`, added `tests/conformance/test_correctness_conditional_group_exists_workflows.py`, and republished `reports/correctness/latest.json`.
- The published combined scorecard now reports 194 cases across 28 manifests with 6 honest `unimplemented` conditional cases.
