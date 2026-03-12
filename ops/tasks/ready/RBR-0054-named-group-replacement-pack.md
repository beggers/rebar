# RBR-0054: Publish a named-group replacement-template correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard past named-group metadata with a bounded named-group replacement-template manifest so the next workflow frontier is explicit before broader grouping or replacement work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/named_group_replacement_workflows.json`
- `tests/conformance/test_correctness_named_group_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows beyond the named-group metadata frontier by adding a dedicated named-group replacement-template manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded named-group replacement observations through the public `rebar` API for tiny literal workflows, including exact cases such as `sub()`/`subn()` with `\\g<name>` templates on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one simple named-group literal replacement path is enough, while named backreferences in patterns, nested named-group interactions, callable replacement semantics for named groups, and broader replacement-template parsing remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed named-group replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0052` and `RBR-0053`.
- This task exists so the worker can expose the next bounded named-group workflow frontier immediately after metadata parity instead of letting the ready queue stop there.
