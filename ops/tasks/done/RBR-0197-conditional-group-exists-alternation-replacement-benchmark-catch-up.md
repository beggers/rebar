# RBR-0197: Catch bounded alternation-heavy two-arm conditional replacement benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded alternation-heavy two-arm conditional replacement workflows supported by `RBR-0196` produce real `rebar` timings before nested replacement-conditioned flows, quantified replacement-conditioned conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded replacement workflows already supported by `RBR-0196`, anchored by a new numbered `module.sub()` or `module.subn()` row for `a(b)?c(?(1)(de|df)|(eg|eh))` and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported alternation-heavy two-arm conditional replacement workflows while leaving replacement templates that read captures, callable replacements, quantified repeats, nested conditionals, branch-local backreferences inside the alternations, and broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0196`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0196`.
- Keep this slice in the existing `conditional_group_exists_boundary` manifest rather than inventing a second benchmark family for the same bounded two-arm conditional surface.
- This task exists so the queue does not reach bounded alternation-heavy two-arm conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.

## Completion Notes
- Replaced the single alternation-heavy replacement gap anchor in `benchmarks/workloads/conditional_group_exists_boundary.json` with eight measured numbered and named `sub()`/`subn()` module and compiled-`Pattern` rows covering the bounded `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` replacement slice.
- Kept replacement-template, callable-replacement, nested replacement-conditioned, and quantified replacement-conditioned rows explicit as remaining known gaps in the same manifest.
- Refreshed `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py` and republished `reports/benchmarks/latest.json`; the combined benchmark scorecard now reports 342 workloads, 293 measured timings, and 49 explicit known gaps.
