# RBR-0236: Catch bounded wider ranged-repeat quantified-group alternation benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded wider ranged-repeat quantified-group alternation workflows already demonstrated by `RBR-0234` produce real `rebar` timings before open-ended repeats, conditional combinations, or broader backtracking-heavy grouped execution reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `wider-ranged-repeat-quantified-group-boundary` manifest to exercise only the bounded workflows already supported by the passing `RBR-0234` slice, anchored by the existing named `pattern.fullmatch` wider ranged-repeat grouped-alternation gap row for `a(?P<word>bc|de){1,3}d` and any directly adjacent numbered, compile, or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported wider ranged-repeat quantified-group alternation workflows while leaving broader counted ranges, open-ended repeats, conditional combinations, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already exercised successfully in `RBR-0234`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0234`; the planned parity follow-on was retired because the newly published slice already passes end to end.
- Keep this slice in the existing `wider_ranged_repeat_quantified_group_boundary` manifest rather than inventing a second benchmark family for the same bounded wider ranged-repeat quantified-group alternation surface.
- This task exists so the queue does not reach wider ranged-repeat quantified-group alternation parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Updated `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` so the seven measured rows now benchmark the bounded `a(bc|de){1,3}d` / `a(?P<word>bc|de){1,3}d` grouped-alternation slice directly, while broader `{1,4}`, open-ended `{1,}`, conditional-combination, and broader backtracking-heavy grouped shapes remain explicit known gaps.
- Refreshed `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` to assert the alternation workload ids and the current 29-manifest combined benchmark totals.
- Republished `reports/benchmarks/latest.json`; the combined scorecard remains at 406 workloads with 371 measured timings and 35 explicit known gaps, and the wider ranged-repeat grouped-alternation manifest now reports 11 workloads with 7 measured timings and 4 explicit gaps.
