# RBR-0261: Catch broader-range open-ended quantified-group alternation backtracking-heavy benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the broader-range open-ended grouped backtracking-heavy `{2,}` workflows supported by `RBR-0260` produce real `rebar` timings without leaving the new slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the explicit broader-range grouped-backtracking known-gap anchor added by `RBR-0255` into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported broader-range open-ended grouped backtracking-heavy workflows while leaving broader grouped conditionals, replacement semantics, and deeper grouped execution shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0260`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0260`.
- Reuse the broader-range grouped-backtracking anchor added by `RBR-0255` instead of forking another manifest.
- This task exists so the queue does not reach broader-range open-ended grouped backtracking-heavy parity and then leave that newly supported slice absent from benchmark reporting.
