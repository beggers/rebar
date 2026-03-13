# RBR-0222: Publish a bounded quantified-alternation backtracking-heavy correctness pack

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that combine a `{1,2}` quantified alternation with overlapping `b|bc` branches so quantified alternation reopens one exact backtracking-heavy follow-on before wider counted ranges or open-ended repeats resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_backtracking_heavy_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified-alternation backtracking-heavy manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(b|bc){1,2}d` and `a(?P<word>b|bc){1,2}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes like `abd` and `abcd`, second-repetition successes like `abbd`, `abbcd`, `abcbd`, and `abcbcd`, plus explicit no-match observations like `abccd` so the scorecard documents the bounded overlapping-branch frontier honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,2}` envelope around one overlapping `b|bc` alternation site is enough, while wider counted ranges, open-ended repeats, branch-local backreferences, conditionals, replacement semantics, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified-alternation backtracking-heavy behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0125`, `RBR-0126`, and `RBR-0221`.
- This task exists so the queue reopens after the quantified-alternation nested-branch trio with one exact overlapping-branch follow-on that is already represented by an explicit benchmark-gap anchor.
