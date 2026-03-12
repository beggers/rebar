# RBR-0101: Publish a bounded optional-group alternation correctness pack

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded optional-group alternation manifest so quantified execution combines one optional quantifier and one grouped alternation before conditionals or broader backtracking work resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/optional_group_alternation_workflows.json`
- `tests/conformance/test_correctness_optional_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated optional-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for tiny literal workflows with one optional capturing group whose body contains one literal alternation site, such as `a(b|c)?d` and `a(?P<word>b|c)?d`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the branch-selected and group-omitted outcomes for that exact optional alternation shape, including the observable match-object group values exposed when the optional capture is absent.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one optional capturing group containing one literal alternation site inside literal prefix/suffix text is enough, while exact or ranged quantified alternation, replacement semantics, branch-local backreferences inside quantified alternation, conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed optional-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0069`, `RBR-0093`, and `RBR-0100`.
- This task exists so the worker can combine already-supported optional quantifier and grouped-alternation semantics before conditionals or broader backtracking reopen the frontier.
- Added `optional-group-alternation-workflows` as the twenty-seventh published correctness manifest with six bounded `a(b|c)?d` / `a(?P<word>b|c)?d` cases covering compile metadata, present-branch module calls, and absent-group pattern calls.
- Regenerated `reports/correctness/latest.json`; the combined published scorecard now reports 188 total cases with 182 passes, 0 explicit failures, and 6 honest `unimplemented` optional-group alternation outcomes.
