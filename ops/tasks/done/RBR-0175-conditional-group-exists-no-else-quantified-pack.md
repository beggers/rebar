# RBR-0175: Publish a bounded quantified omitted-no-arm conditional correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified omitted-no-arm conditional manifest so repeated accepted no-else behavior becomes explicit instead of living only as a benchmark gap row.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_no_else_quantified_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_no_else_quantified_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified omitted-no-arm manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded observations through the public `rebar` API for one optional numbered or named capture whose omitted-no-arm conditional site is quantified exactly twice, such as `a(b)?c(?(1)d){2}` and `a(?P<word>b)?c(?(word)d){2}`, on module and compiled-`Pattern` paths that CPython already supports.
- The published cases cover the bounded capture-present and capture-absent outcomes for that exact shape, including haystacks that require `dd` when the capture is present and capture-absent haystacks that still succeed because the omitted no arm contributes nothing at both repetitions.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the omitted-no-arm conditional is enough, while explicit-empty-else, two-arm, or empty-arm quantified conditionals, replacement semantics, alternation inside the repeated arm, nested conditionals inside the repeated site, ranged or open-ended repeats, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified omitted-no-arm behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0174`, `RBR-0147`, and `RBR-0150`.
- This task exists so the queue reopens quantified omitted-no-arm composition through one exact accepted slice instead of leaving it as a benchmark-only gap row.

## Completion
- Added `conditional_group_exists_no_else_quantified_workflows.json` as a dedicated eight-case manifest covering numbered and named `{2}` omitted-no-arm conditional compile, module-call, and pattern-call observations.
- Wired the new manifest into the default correctness harness, added a focused regression test, and republished `reports/correctness/latest.json`; the combined published scorecard now reports 380 cases across 52 manifests with 372 passes and 8 explicit `unimplemented` outcomes for this newly published slice.
