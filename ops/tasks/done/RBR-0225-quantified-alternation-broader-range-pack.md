# RBR-0225: Publish a bounded broader-range quantified-alternation correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for workflows that widen quantified alternation from `{1,2}` to `{1,3}` so counted quantified alternation broadens one exact step before open-ended repeats resume.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.json`
- `tests/conformance/test_correctness_quantified_alternation_broader_range_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range quantified-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(b|c){1,3}d` and `a(?P<word>b|c){1,3}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes like `abd` and `acd`, third-repetition successes like `abbbd`, `abccd`, and `abcbd`, plus explicit no-match observations like `ad` and `abbbcd` so the scorecard documents the widened counted-range frontier honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one bounded `{1,3}` envelope around one `b|c` alternation site is enough, while wider counted ranges, open-ended repeats, nested alternation, branch-local backreferences, conditionals, replacement semantics, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range quantified-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0224`.
- This task exists so the queue broadens quantified alternation through one exact `{1,3}` follow-on with an existing benchmark-gap anchor instead of jumping directly to open-ended repeats.

## Completion
- Added `quantified_alternation_broader_range_workflows.json` to the default correctness fixture pack and published a dedicated 16-case `{1,3}` broader-range manifest covering numbered and named compile, lower-bound module search, third-repetition fullmatch, and explicit no-match workflows for `a(b|c){1,3}d` / `a(?P<word>b|c){1,3}d`.
- Added a focused correctness regression test that locks the CPython observations for the new pack while allowing the current `rebar` outcome to remain either `unimplemented` or a future `pass`, so `RBR-0226` can flip the same cases without rewriting the publication test.
- Regenerated `reports/correctness/latest.json`; the published combined scorecard now reports 532 cases total with 516 passes and 16 honest `unimplemented` broader-range quantified-alternation gaps.
