# RBR-0264: Publish a nested open-ended quantified-group alternation correctness pack

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published correctness scorecard with one bounded nested open-ended grouped-alternation manifest so the next milestone reopens the regex surface through a broader grouped shape immediately after `RBR-0263` consolidated the adjacent Python parity harness.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.json`
- `tests/conformance/test_correctness_nested_open_ended_quantified_group_alternation_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The combined correctness report grows by adding a dedicated nested open-ended quantified-group alternation manifest instead of replacing any existing fixture pack.
- The new manifest captures bounded numbered and named compile, module, and compiled-`Pattern` observations for `a((bc|de){1,})d` and `a(?P<outer>(bc|de){1,})d` that CPython already accepts.
- The published cases include lower-bound successes such as `abcd` and `aded`, repeated and mixed-branch successes such as `abcbcded` and `adededed`, plus explicit no-match observations like `ae` or a haystack whose grouped repetition does not satisfy the trailing `d`.
- The new cases are reported honestly as `pass` or `unimplemented`; they must not disappear from the scorecard just because current `rebar` behavior is incomplete.
- The pack stays narrow and explicit: one outer capture around one open-ended `(bc|de){1,}` site is enough, while broader counted ranges like `{1,4}`, grouped conditionals, grouped backtracking-heavy follow-ons, replacement workflows, and broader nested grouped execution remain out of scope unless a case is included specifically to document them as honest gaps.

## Constraints
- Keep this task focused on harness publication, fixtures, and scorecard regeneration; do not silently broaden runtime behavior just to make the new cases pass.
- Do not delegate any newly observed nested open-ended grouped-alternation behavior to stdlib `re` outside the existing differential harness path.
- Preserve the published combined-scorecard contract for `reports/correctness/latest.json`.

## Notes
- Build on `RBR-0263`.
- Keep the later benchmark catch-up for this slice anchored to the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family when follow-on parity and benchmark tasks are seeded.

## Completion
- 2026-03-13: Added `nested-open-ended-quantified-group-alternation-workflows` to the default correctness fixture set, published a new 14-case nested grouped `{1,}` manifest plus focused conformance coverage, and republished `reports/correctness/latest.json` at 691 total cases across 80 manifests with 677 passes, 0 explicit failures, and 14 honest `unimplemented` outcomes for this newly published slice.
