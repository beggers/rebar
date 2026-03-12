# RBR-0079: Catch nested-group benchmarks up with the new bounded slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded nested-group workflows supported by `RBR-0078` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/nested_group_boundary.json`
- `tests/benchmarks/test_nested_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated nested-group manifest that exercises only the bounded workflows already supported by `RBR-0078`, such as `a((b))d` and `a(?P<outer>(?P<inner>b))d` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested-group workflows while leaving broader nested-group, alternation-in-nesting, or quantified-group shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0078`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0078`.
- This task exists so the queue does not reach bounded nested-group parity and then leave that newly supported slice absent from benchmark reporting.
