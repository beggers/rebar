# RBR-0073: Catch grouped-alternation replacement benchmarks up with the new combined slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded grouped-alternation replacement workflows supported by `RBR-0072` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_alternation_replacement_boundary.json`
- `tests/benchmarks/test_grouped_alternation_replacement_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated grouped-alternation replacement manifest that exercises only the bounded `sub()` and `subn()` workflows already supported by `RBR-0072`, such as `a(b|c)d` with `\\1x` and `a(?P<word>b|c)d` with `\\g<word>x` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported grouped-alternation replacement workflows while leaving broader grouped, alternation, or replacement-template shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0072`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0070` and `RBR-0072`.
- This task exists so the queue does not reach grouped-alternation replacement parity and then leave that newly supported combined slice absent from benchmark reporting.
