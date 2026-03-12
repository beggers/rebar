# RBR-0123: Catch bounded wider ranged-repeat quantified-group benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the wider ranged-repeat quantified-group workflows supported by `RBR-0122` produce real `rebar` timings before quantified alternation or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated manifest that exercises only the bounded wider ranged-repeat workflows already supported by `RBR-0122`, such as `a(bc){1,3}d` and `a(?P<word>bc){1,3}d`, through module and compiled-`Pattern` entrypoints, including representative lower-bound and third-repetition haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported wider ranged-repeat workflows while leaving still-wider counted ranges, open-ended repeats, quantified alternation inside repeated groups, conditional combinations, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0122`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0122`.
- This task exists so the queue does not leave the next wider counted-range slice measured only in correctness reporting.

## Completion
- Added `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` and wired it into the default benchmark manifest set so the bounded `{1,3}` numbered and named quantified-group compile/search/fullmatch workflows now publish real `rebar` timings.
- Regenerated `reports/benchmarks/latest.json`; the published combined benchmark scorecard now reports 240 workloads with 182 measured `rebar` timings and 58 explicit known gaps, including new wider-ranged-repeat gap rows for broader counted ranges, open-ended repeats, quantified alternation, conditional composition, and backtracking-heavy shapes.
- Added `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` and refreshed the adjacent exact/ranged benchmark assertions after shifting their carry-forward broader-range gap rows from `{1,3}` to `{1,4}` so the benchmark surface no longer publishes the same `{1,3}` slice as both measured and unsupported.
