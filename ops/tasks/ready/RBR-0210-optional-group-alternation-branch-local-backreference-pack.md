# RBR-0210: Publish a bounded optional-group-alternation-plus-branch-local-backreference correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine an optional grouped alternation with a same-branch backreference so the next anchored post-`RBR-0209` frontier is explicit before broader counted-repeat backtracking work resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/optional_group_alternation_branch_local_backreference_workflows.json`
- `tests/conformance/test_correctness_optional_group_alternation_branch_local_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated optional-group-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b|c)\\2)?d` and `a(?P<outer>(?P<inner>b|c)(?P=inner))?d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include explicit absent-group successes like `ad`, present-branch successes like `abbd` and `accd`, and explicit no-match observations like `abd` so the scorecard documents that the optional group may be omitted entirely but, when present, the selected branch still must satisfy the later backreference.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one optional group containing one literal alternation followed by one same-branch backreference is enough, while counted repeats beyond `?`, replacement semantics, conditionals, nested alternations, callable replacement behavior, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed optional-group-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0090`, `RBR-0091`, `RBR-0101`, `RBR-0102`, `RBR-0103`, and `RBR-0209`.
- This task exists so the queue continues from the quantified branch-local frontier into the smallest remaining optional quantified follow-on with an existing benchmark anchor instead of jumping directly to broader counted-repeat quantified-alternation-plus-backreference work.
