# RBR-0145: Publish a bounded nested omitted-no-arm conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded omitted-no-arm nested-conditional manifest so the queue broadens accepted conditional composition through an exact CPython-supported slice instead of reopening a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_no_else_nested_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_no_else_nested_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated omitted-no-arm nested-conditional manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose omitted-no-arm conditional yes-arm contains one nested omitted-no-arm conditional site, such as `a(b)?c(?(1)(?(1)d))` and `a(?P<word>b)?c(?(word)(?(word)d))`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded success and failure outcomes for that exact shape, including capture-present haystacks that require the nested `d` suffix and capture-absent haystacks that match because the outer omitted-no-arm conditional contributes no suffix.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one nested omitted-no-arm conditional site inside the outer yes-arm is enough, while replacement semantics, empty-arm variants, quantified conditionals, alternation inside the nested arms, deeper nesting, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested-conditional behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0144` and the already-landed omitted-no-arm conditional baseline in `RBR-0108` and `RBR-0131`.
- This task exists so the queue keeps accepted conditional composition explicit instead of jumping straight from single-site conditionals to quantified conditionals or a vague broader-backtracking bucket.

## Completion
- Added `conditional_group_exists_no_else_nested_workflows.json` with eight bounded numbered and named nested omitted-no-arm conditional cases covering compile metadata, present-capture success, present-capture missing-suffix failure, and absent-capture success.
- Wired the manifest into the default correctness harness, added a regression test that asserts the new cases publish as honest `unimplemented` gaps under the current Rust-backed frontier, and regenerated `reports/correctness/latest.json` to `288` total cases with `8` explicit unimplemented nested-conditional gaps.
- Updated the neighboring default-harness regression tests whose combined-scorecard totals changed from the new manifest.
