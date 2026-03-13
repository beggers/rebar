# RBR-0267: Publish a broader-range wider-ranged-repeat quantified-group alternation correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded broader `{1,4}` grouped-alternation manifest so the counted-repeat frontier reopens immediately after `RBR-0266` closed benchmark catch-up for the nested open-ended `{1,}` slice.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated broader-range wider-ranged-repeat grouped-alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a(bc|de){1,4}d` and `a(?P<word>bc|de){1,4}d` that CPython already accepts.
- The published cases include lower-bound successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcbcded` and `adedededed`, plus explicit no-match observations like `ad` or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one broader counted `{1,4}` envelope around `(bc|de)` is enough, while open-ended repeats, grouped conditionals, replacement workflows, nested grouped alternation, and broader grouped backtracking remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed broader-range wider-ranged-repeat grouped-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0266`.
- Keep the eventual benchmark catch-up for this slice anchored to the existing `module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family when follow-on parity and benchmark tasks are seeded.

## Completion
- Added `broader-range-wider-ranged-repeat-quantified-group-alternation-workflows` to the default correctness manifest set with 10 numbered and named compile/module/pattern observations covering lower-bound hits on `abcd` and `aded`, mixed and upper-bound hits on `abcbcded`, `adedededed`, and `abcbcdeded`, plus explicit `ad` and fifth-repetition overflow no-match cases.
- Added `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py` to pin the combined-scorecard suite ids, family list, and CPython-visible observations for the new `{1,4}` grouped-alternation pack.
- Republished `reports/correctness/latest.json`; the combined correctness scorecard now covers 81 manifests / 701 cases, with this new broader `{1,4}` grouped-alternation slice remaining explicit as 10 honest `unimplemented` cases and no explicit failures.
