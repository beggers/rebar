# RBR-0064: Catch grouped-segment benchmarks up with the new literal-segment slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded grouped-segment workflows supported by `RBR-0063` produce real `rebar` timings before the queue reopens a new correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_segment_boundary.json`
- `tests/benchmarks/test_grouped_segment_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated grouped-segment manifest that exercises only the bounded literal prefix/suffix workflows already supported by `RBR-0063`, such as `a(b)c` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported grouped-segment workflows while leaving any still-unsupported grouped shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0063`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0061` and `RBR-0063`.
- This task exists so the queue does not reach grouped-segment parity and then leave that newly supported surface absent from benchmark reporting.
