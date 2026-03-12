# RBR-0052: Publish a named-group correctness pack

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard past the first grouped numbered-capture slice with a bounded named-group manifest so the next compatibility frontier stays explicit before broader grouping or syntax work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/named_group_workflows.json`
- `tests/conformance/test_correctness_named_group_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows beyond the grouped numbered-capture frontier by adding a dedicated named-group manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded named-group observations through the public `rebar` API for tiny literal workflows, including explicit compile or match metadata such as `groupindex`, `group("name")`, `groupdict()`, and `span("name")` on exact module or `Pattern` cases that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one simple named-group literal path is enough, while named backreferences, conditional groups, nested named-group interactions, and replacement-template behavior remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed named-group behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0050` and `RBR-0051`.
- This task exists so the worker can expose the next bounded grouping frontier immediately after numbered-capture parity instead of letting the ready queue stop there.
