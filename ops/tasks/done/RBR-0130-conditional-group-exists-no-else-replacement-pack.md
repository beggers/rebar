# RBR-0130: Publish a bounded omitted-no-arm conditional replacement correctness pack

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published correctness scorecard with a bounded omitted-no-arm conditional replacement manifest so the queue combines an already-landed conditional slice with already-landed replacement helpers before nested or quantified conditionals reopen the frontier.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_no_else_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_no_else_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated omitted-no-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for tiny literal workflows using `sub()` and `subn()` with simple replacement strings on `a(b)?c(?(1)d)` and `a(?P<word>b)?c(?(word)d)` through module and compiled-`Pattern` entrypoints that CPython already supports.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one omitted-no-arm conditional site feeding constant replacement text is enough, while explicit-empty-else or fully-empty variants, replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0108` and `RBR-0109`.
- This task exists so the queue reopens after `RBR-0129` with the smallest existing conditional-replacement gap instead of jumping straight to nested conditionals, quantified conditionals, or a vague broader-backtracking bucket.

## Completion
- Added `tests/conformance/fixtures/conditional_group_exists_no_else_replacement_workflows.json` with eight bounded `sub()`/`subn()` module and compiled-`Pattern` cases for numbered and named omitted-no-arm conditional replacements.
- Wired the manifest into `python/rebar_harness/correctness.py` so the default combined publication now includes the new conditional replacement pack.
- Added `tests/conformance/test_correctness_conditional_group_exists_no_else_replacement_workflows.py` and refreshed default-report assertions in `tests/conformance/test_correctness_conditional_group_exists_empty_else_alternation_workflows.py` plus `tests/python/test_readme_reporting.py`.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 248 total cases across 37 manifests with 240 passes and 8 honest `unimplemented` outcomes for the newly published conditional replacement slice.
- Verified with `python3 -m unittest tests.conformance.test_correctness_conditional_group_exists_no_else_replacement_workflows tests.conformance.test_correctness_conditional_group_exists_empty_else_alternation_workflows tests.python.test_readme_reporting`.
