# RBR-0153: Catch bounded nested explicit-empty-else conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded nested explicit-empty-else conditional workflows supported by `RBR-0152` produce real `rebar` timings before broader nested conditional expansion reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_empty_else_boundary` manifest and converts its explicit nested-conditional gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0152`, such as `a(b)?c(?(1)(?(1)d)|)` and `a(?P<word>b)?c(?(word)(?(word)d)|)`, through module and compiled-`Pattern` entrypoints with representative capture-present and capture-absent haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested explicit-empty-else conditional workflows while leaving empty-yes-arm or fully-empty nested variants, quantified conditionals, replacement-conditioned helpers, deeper nesting, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0152`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0152`.
- Use the existing `module-search-numbered-nested-conditional-group-exists-empty-else-cold-gap` row in `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded nested explicit-empty-else parity and then leave that newly supported slice absent from benchmark reporting.
- Completed by replacing the single nested explicit-empty-else gap anchor with four measured numbered/named module-search and `Pattern.fullmatch()` workloads for `a(b)?c(?(1)(?(1)d)|)` and `a(?P<word>b)?c(?(word)(?(word)d)|)`, updating the benchmark assertions, and republishing `reports/benchmarks/latest.json` at 293 total workloads with 239 real `rebar` timings and 54 explicit known gaps in this checkout.
