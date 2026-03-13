# RBR-0216: Publish a bounded quantified-alternation-plus-conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a `{1,2}` quantified alternation with a later group-exists conditional so quantified alternation reopens conditional composition through one exact follow-on before broader counted-repeat backtracking resumes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_conditional_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_conditional_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-alternation-plus-conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a((b|c){1,2})?(?(1)d|e)` and `a(?P<outer>(b|c){1,2})?(?(outer)d|e)` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include absent-group successes like `ae`, lower-bound present successes like `abd` and `acd`, second-repetition successes like `abbd`, `accd`, and `abcd`, plus explicit no-match observations like `abe` and `acce` so the scorecard documents that the conditional yes arm still requires `d` once the quantified alternation participates.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one optional capture around one `{1,2}` quantified alternation followed by one group-exists conditional is enough, while branch-local backreferences, replacement semantics, nested conditionals, wider counted ranges, open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-alternation-plus-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0125`, `RBR-0126`, and `RBR-0215`.
- This task exists so the queue reopens after the branch-local sequence with one exact conditional follow-on that is already represented by an explicit benchmark-gap anchor.
- Completed 2026-03-13: added the dedicated `quantified_alternation_conditional_workflows.json` manifest, wired it into the default correctness harness, added a conformance test that accepts either `pass` or honest `unimplemented` for the new slice, and regenerated `reports/correctness/latest.json` with the new published cases.
