# RBR-0201: Publish a bounded quantified two-arm conditional replacement correctness pack

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded quantified two-arm conditional replacement manifest so replacement-conditioned work reopens quantified composition through one exact follow-on instead of a vague broader-backtracking bucket.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_replacement_workflows.json`
- `tests/conformance/test_correctness_conditional_group_exists_quantified_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated quantified two-arm conditional replacement manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded replacement observations through the public `rebar` API for one optional numbered or named capture whose two-arm conditional site is quantified exactly twice, such as `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`, on module and compiled-`Pattern` `sub()` or `subn()` paths that CPython already supports.
- The published cases cover the bounded capture-present and capture-absent outcomes for that exact shape, including workflows that require `dd` when the capture is present and `ee` when it is absent before constant replacement text is emitted.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one exact-repeat `{2}` quantifier over the accepted two-arm conditional is enough, while replacement templates that read capture groups, callable replacement semantics, alternation-heavy repeated arms, nested conditionals inside the repeated site, ranged or open-ended repeats, branch-local backreferences, and broader backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed quantified conditional replacement behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0149`, `RBR-0193`, and the existing conditional replacement helper surface.
- This task exists so the queue reopens quantified replacement composition through one exact accepted slice before branch-local-backreference arms or broader backtracking reopen the frontier.

## Completion
- Added `conditional-group-exists-quantified-replacement-workflows` to the default correctness harness, publishing eight bounded numbered and named `sub()`/`subn()` quantified two-arm conditional replacement cases for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`.
- Regenerated `reports/correctness/latest.json`; the combined scorecard now publishes 60 manifests / 448 cases with the new quantified replacement suite reported honestly as 8 `unimplemented` cases pending `RBR-0202`.
- Added the dedicated conformance test for the new manifest and refreshed the affected conditional-group-exists cumulative tests to the new combined report totals.
