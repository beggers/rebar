# RBR-0254: Catch broader-range open-ended quantified-group alternation benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the broader-range open-ended quantified-group alternation `{2,}` workflows supported by `RBR-0253` produce real `rebar` timings before broader grouped-conditionals or deeper grouped backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `module-search-numbered-open-ended-group-broader-range-cold-gap` anchor into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported broader-range open-ended grouped-alternation workflows while leaving broader grouped-conditionals, replacement semantics, and deeper grouped backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0253`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0253`.
- Reuse the existing `module-search-numbered-open-ended-group-broader-range-cold-gap` row as the benchmark anchor instead of forking another manifest.
- This task exists so the queue does not reach broader-range open-ended grouped-alternation parity and then leave that newly supported slice absent from benchmark reporting.
- Completed 2026-03-13: promoted the existing broader-range anchor into a measured workload, added the adjacent numbered and named `{2,}` compile/search/fullmatch rows in `open_ended_quantified_group_boundary.json`, added focused benchmark coverage in `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`, updated combined-suite gap expectations, and regenerated `reports/benchmarks/latest.json` so the broader-range open-ended grouped-alternation slice now publishes real `rebar` timings.
