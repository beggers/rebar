# RBR-0100: Catch ranged-repeat quantified-group benchmarks up with the new bounded slice

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded ranged-repeat quantified-group workflows supported by `RBR-0099` produce real `rebar` timings before quantified alternation, conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated ranged-repeat quantified-group manifest that exercises only the bounded workflows already supported by `RBR-0099`, such as `a(bc){1,2}d` and `a(?P<word>bc){1,2}d` through module and compiled-`Pattern` entrypoints, including representative lower-bound and upper-bound haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported bounded counted-range workflows while leaving wider ranges, open-ended repeats, quantified alternation, conditional, or backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0099`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0099`.
- This task exists so the queue does not reach bounded ranged-repeat quantified-group parity and then leave that newly supported counted-range slice absent from benchmark reporting.
- Added `ranged_repeat_quantified_group_boundary.json` with six measured bounded `{1,2}` workloads and two explicit known-gap rows, wired it into the default benchmark suite, refreshed `reports/benchmarks/latest.json`, and added regression coverage for the combined report counts and manifest metadata.
- Refreshed the adjacent exact-repeat benchmark pack so its forward-looking gap row now tracks a broader `{1,3}` counted-range shape instead of the already-supported `{1,2}` slice.
