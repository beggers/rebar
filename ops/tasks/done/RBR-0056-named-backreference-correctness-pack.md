# RBR-0056: Publish a named-backreference correctness pack

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published correctness scorecard past named-group replacement templates with a bounded named-backreference manifest so the next grouped-reference frontier stays explicit before broader syntax work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/named_backreference_workflows.json`
- `tests/conformance/test_correctness_named_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows beyond the named-group replacement-template frontier by adding a dedicated named-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded named-backreference observations through the public `rebar` API for tiny literal workflows, including exact compile or match cases such as `(?P<word>ab)(?P=word)` on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one simple named-backreference literal path is enough, while numbered backreferences beyond the already-published grouped-capture slice, nested references, alternation-driven backreference semantics, and broader backtracking behavior remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed named-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0054` and `RBR-0055`.
- This task exists so the worker can expose the next bounded grouped-reference frontier immediately after named-group replacement parity instead of letting the ready queue stop there.
- Completed with a new `named-backreference-workflows` correctness manifest covering bounded compile, module `search()`, and compiled-`Pattern.search()` observations for `(?P<word>ab)(?P=word)` without changing runtime behavior.
- Verified with `python3 -m unittest tests.conformance.test_correctness_named_backreference_workflows tests.conformance.test_correctness_named_group_replacement_workflows` and `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
- Republished `reports/correctness/latest.json`; the combined 12-manifest scorecard now reports 96 total cases with 93 passes, 0 failures, and 3 honest `unimplemented` named-backreference gaps.
