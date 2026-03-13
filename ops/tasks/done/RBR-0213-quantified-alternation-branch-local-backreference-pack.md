# RBR-0213: Publish a bounded quantified-alternation-plus-branch-local-backreference correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a `{1,2}` quantified alternation with a same-branch backreference so the next post-`RBR-0212` branch-local frontier stays concrete before broader counted-repeat backtracking resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_branch_local_backreference_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-alternation-plus-branch-local-backreference manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b|c)\\2){1,2}d` and `a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes like `abbd` and `accd`, second-repetition successes like `abbbbd`, `accccd`, and `abbccd`, plus explicit no-match observations like `abcd` so the scorecard documents that each quantified repetition still has to satisfy the same-branch backreference.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one quantified `{1,2}` envelope around one literal alternation site with one same-branch backreference is enough, while broader counted ranges, open-ended repeats, replacement semantics, conditionals, nested alternations, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-alternation-plus-branch-local-backreference behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0125`, `RBR-0126`, and `RBR-0212`.
- This task exists so the queue continues past the optional `?` branch-local slice through one exact `{1,2}` quantified-alternation follow-on instead of jumping directly to broader counted-repeat backtracking.
- Completed 2026-03-13: added `quantified_alternation_branch_local_backreference_workflows.json`, registered it in the default correctness harness, added the matching regression test, and republished `reports/correctness/latest.json` to 482 total cases across 64 manifests with 472 passes and 10 honest `unimplemented` outcomes for this new slice.
