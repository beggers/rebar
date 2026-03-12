# RBR-0070: Catch grouped-alternation benchmarks up with the new combined slice

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded grouped-alternation workflows supported by `RBR-0069` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_alternation_boundary.json`
- `tests/benchmarks/test_grouped_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated grouped-alternation manifest that exercises only the bounded literal workflows already supported by `RBR-0069`, such as `a(b|c)d` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported grouped-alternation workflows while leaving broader grouped or alternation shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0069`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0067` and `RBR-0069`.
- This task exists so the queue does not reach grouped-alternation parity and then leave that newly supported combined slice absent from benchmark reporting.
- Completed with a new `grouped-alternation-boundary` manifest, default-suite wiring, honest nested-group gap cleanup in older manifests, a combined benchmark regression test, and a republished `reports/benchmarks/latest.json` at 84 workloads with 65 measured timings and 19 explicit gaps.
