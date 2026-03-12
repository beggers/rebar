# RBR-0085: Catch nested-group callable-replacement benchmarks up with the new bounded slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded nested-group callable-replacement workflows supported by `RBR-0084` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/nested_group_callable_replacement_boundary.json`
- `tests/benchmarks/test_nested_group_callable_replacement_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated nested-group callable-replacement manifest that exercises only the bounded `sub()` and `subn()` callable workflows already supported by `RBR-0084`, such as `a((b))d` and `a(?P<outer>(?P<inner>b))d` with callables that read the published numbered or named capture values through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested-group callable-replacement workflows while leaving broader nested-group, alternation-in-nesting, quantified-group, or callback shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0084`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0084`.
- This task exists so the queue does not reach bounded nested-group callable-replacement parity and then leave that newly supported slice absent from benchmark reporting.
