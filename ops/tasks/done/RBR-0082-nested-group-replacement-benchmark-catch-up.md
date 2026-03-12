# RBR-0082: Catch nested-group replacement benchmarks up with the new bounded slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded nested-group replacement workflows supported by `RBR-0081` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/nested_group_replacement_boundary.json`
- `tests/benchmarks/test_nested_group_replacement_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated nested-group replacement manifest that exercises only the bounded workflows already supported by `RBR-0081`, such as `a((b))d` and `a(?P<outer>(?P<inner>b))d` through module and compiled-`Pattern` `sub()` or `subn()` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested-group replacement workflows while leaving broader nested-group, alternation-in-nesting, quantified-group, or callable-replacement shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0081`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0081`.
- This task exists so the queue does not reach bounded nested-group replacement parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added `benchmarks/workloads/nested_group_replacement_boundary.json` and wired it into the default combined benchmark manifest set so bounded numbered and named nested-group `sub()`/`subn()` workflows now publish real `rebar` timings alongside explicit callable and quantified nested replacement gap rows.
- Added `tests/benchmarks/test_nested_group_replacement_boundary_benchmarks.py`, updated the combined nested-group benchmark expectations, and regenerated `reports/benchmarks/latest.json`; the published combined benchmark report now covers 122 workloads with 95 measured `rebar` timings and 27 explicit known gaps.
