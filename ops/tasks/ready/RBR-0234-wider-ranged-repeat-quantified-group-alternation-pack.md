# RBR-0234: Publish a bounded wider ranged-repeat quantified-group alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for grouped alternation inside a wider `{1,3}` counted repeat so the queue widens the already-supported ranged-repeat envelope before open-ended repeats, conditional combinations, or broader backtracking-heavy grouped execution resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated wider ranged-repeat quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(bc|de){1,3}d` and `a(?P<word>bc|de){1,3}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcded`, `abcbcded`, and `adededed`, plus explicit no-match observations like `ad` or `abcbcbcbcd` so the scorecard documents the wider ranged-repeat grouped-alternation frontier honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,3}` envelope around one `bc|de` alternation site is enough, while broader counted ranges, open-ended repeats, conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed wider ranged-repeat quantified-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0123` and `RBR-0233`.
- This task exists so the queue reuses the already-published wider-ranged-repeat grouped-alternation benchmark anchor instead of stopping after the exact-repeat counted-repeat alternation slice.
