# RBR-0080: Publish a nested-group replacement correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded nested-group replacement manifest so the next combined nesting-and-replacement frontier is explicit before quantified branches, branch-local backreferences, or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_replacement_workflows.json`
- `tests/conformance/test_correctness_nested_group_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested-group replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows with one capture nested inside another, such as `sub()` or `subn()` using `a((b))d` with `\\1x` or `\\2x`, and `a(?P<outer>(?P<inner>b))d` with `\\g<outer>x` or `\\g<inner>x`, on module and compiled-`Pattern` paths that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested capture site inside literal prefix/suffix text feeding a replacement template is enough, while nested alternation, quantified groups, callable replacement behavior, branch-local backreferences, broader template parsing, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-group replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0078` and `RBR-0079`.
- This task exists so the worker can expose the next concrete gap after bounded nested-group match parity without jumping straight to quantified branches or broader backtracking.

## Completion
- Added `tests/conformance/fixtures/nested_group_replacement_workflows.json` and wired it into `python/rebar_harness/correctness.py` so the combined scorecard now publishes a dedicated nested-group replacement manifest.
- Added `tests/conformance/test_correctness_nested_group_replacement_workflows.py` and regenerated `reports/correctness/latest.json`; the published combined correctness report now covers 144 cases across 20 manifests with 136 passes and 8 explicit `unimplemented` nested-group replacement outcomes.
- Kept runtime behavior unchanged: the new numbered and named nested-group replacement-template cases document the current unsupported frontier through honest `unimplemented` results instead of silently broadening execution semantics.
