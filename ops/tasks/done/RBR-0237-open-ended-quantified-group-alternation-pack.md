# RBR-0237: Publish a bounded open-ended quantified-group alternation correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for grouped alternation inside an open-ended `{1,}` counted repeat so the queue carries the grouped counted-repeat frontier through the same open-ended envelope already supported for simpler quantified alternation.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_open_ended_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated open-ended quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(bc|de){1,}d` and `a(?P<word>bc|de){1,}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes such as `abcd` and `aded`, repeated and mixed-branch successes such as `abcbcd`, `abcded`, `abcbcded`, and `adededed`, plus explicit no-match observations like `ad` or an invalid-branch haystack so the scorecard documents the bounded open-ended grouped-alternation frontier honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{1,}` envelope around one `bc|de` alternation site is enough, while broader counted-repeat families, conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed open-ended quantified-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0236`.
- This task exists so grouped alternation reaches the same bounded open-ended counted-repeat envelope already proven for simpler quantified alternation instead of stopping at the wider `{1,3}` slice.
- Completed 2026-03-13: added a dedicated 16-case open-ended grouped-alternation correctness manifest covering numbered and named compile/module/compiled-pattern observations for `a(bc|de){1,}d` and `a(?P<word>bc|de){1,}d`, added focused regression coverage, and republished `reports/correctness/latest.json` to the combined 72-manifest / 584-case scorecard with 16 honest `unimplemented` outcomes for this newly published slice.
