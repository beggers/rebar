# RBR-0252: Publish a broader-range open-ended quantified-group alternation correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded manifest for grouped alternation inside a broader-range open-ended `{2,}` counted repeat so the grouped counted-repeat frontier shifts the lower bound beyond the landed `{1,}` slice before broader grouped-conditionals or deeper backtracking reopen it.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range open-ended quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for the exact numbered and named workflows `a(bc|de){2,}d` and `a(?P<word>bc|de){2,}d` on compile, module, and compiled-`Pattern` paths that CPython already supports.
- The published cases include lower-bound successes such as `abcbcd` and `adeded`, mixed-branch successes such as `abcded` and `abcbcded`, one bounded fourth-repetition success such as `adededed`, plus explicit no-match observations like `abcd` or `ad` so the scorecard documents the shifted open-ended lower bound honestly.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one open-ended `{2,}` envelope around one `bc|de` alternation site is enough, while broader grouped-conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, and deeper backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range open-ended quantified-group alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0251`.
- This task exists so grouped alternation broadens the open-ended lower bound through one exact `{2,}` follow-on with an existing benchmark-gap anchor instead of jumping to a vaguer grouped-conditional or deeper-backtracking bucket.
- Completed 2026-03-13: added the dedicated `{2,}` grouped-alternation correctness manifest and conformance test, regenerated `reports/correctness/latest.json`, and published the new 16-case suite honestly as `unimplemented` pending `RBR-0253`.
