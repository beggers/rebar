# RBR-0207: Publish a bounded quantified branch-local-backreference correctness pack

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a quantified branch-local capture with a later backreference so branch-local work reopens quantified composition through one exact follow-on before broader backtracking resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_branch_local_backreference_workflows.json`
- `tests/conformance/test_correctness_quantified_branch_local_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b)+|c)\\2d` and `a(?P<outer>(?P<inner>b)+|c)(?P=inner)d` on module and compiled-`Pattern` paths that CPython already supports.
- The published cases include successful quantified-capture paths on tiny haystacks like `abbd` and `abbbd` plus explicit no-match observations for the `c` branch so the scorecard documents that an unresolved branch-local backreference still fails after the alternation chooses the noncapturing branch.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one `+`-quantified inner capture inside one alternation branch followed by one later backreference is enough, while conditionals, replacement semantics, callable replacement behavior, nested alternations, wider quantified shapes, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0090`, `RBR-0091`, and `RBR-0206`.
- This task exists so the queue reopens after `RBR-0206` through one exact quantified branch-local follow-on instead of jumping directly to a vague broader-backtracking bucket.
- Added `quantified-branch-local-backreference-workflows` to the default correctness fixture set with eight bounded compile/module/pattern cases covering numbered and named `a((b)+|c)\\2d` and `a(?P<outer>(?P<inner>b)+|c)(?P=inner)d` observations on `abbd`, `abbbd`, and the failing `acd` branch.
- Regenerated `reports/correctness/latest.json`; the combined published scorecard is now 462 total cases across 62 manifests with 454 passes, 0 explicit failures, and 8 honest `unimplemented` outcomes queued for `RBR-0208`.
