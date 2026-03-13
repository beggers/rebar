# RBR-0231: Publish a bounded exact-repeat quantified-group alternation correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for grouped alternation inside an exact-repeat quantified capture so the queue leaves the quantified-alternation `{1,}` follow-on and then widens one already-anchored counted-repeat alternation slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/exact_repeat_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated exact-repeat quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(bc|de){2}d` and `a(?P<word>bc|de){2}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include deterministic two-repetition successes such as `abcbcd`, `abcded`, and `adeded`, plus at least one explicit no-match observation like `abcd` or `abcbcbcd` so the scorecard documents the alternation-bearing exact-repeat frontier honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact `{2}` envelope around one `bc|de` alternation site is enough, while ranged repeats, open-ended repeats, conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed exact-repeat quantified-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0230`.
- This task exists so the queue reuses an already-published benchmark-gap anchor for grouped alternation inside a deterministic counted repeat instead of inventing a looser post-quantified-alternation bucket.
