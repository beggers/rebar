# RBR-0204: Publish a bounded conditional-plus-branch-local-backreference correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a branch-local backreference with a group-exists conditional so the next combined branch-local/conditional frontier is explicit before broader backtracking work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_branch_local_backreference_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_branch_local_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated conditional-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b)|c)\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include the successful capture-present path on tiny haystacks like `abbd` plus explicit no-match observations for the `c` branch so the scorecard documents the CPython rule that the unresolved branch-local backreference prevents the later else arm from rescuing the match.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one branch-local capture site followed by one backreference and one group-exists conditional is enough, while quantified branches, replacement semantics, callable replacement behavior, nested conditionals, alternation-heavy follow-ons, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0090`, `RBR-0091`, and `RBR-0182`.
- This task exists so the queue reopens after `RBR-0203` through one exact combined branch-local/conditional slice that already has a stored benchmark anchor instead of jumping directly to a vague broader-backtracking bucket.

## Completion
- Added `conditional-group-exists-branch-local-backreference-workflows` to the default correctness fixture set with six bounded numbered/named compile, module-search, and pattern-fullmatch cases for `a((b)|c)\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)`.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports 61 manifests, 454 total cases, 448 passes, and 6 honest `unimplemented` results for this new slice.
- Added a dedicated regression test for the new manifest and updated default combined-scorecard tests to expect the expanded published totals.
