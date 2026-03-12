# RBR-0129: Catch bounded alternation-heavy explicit-empty-else conditional benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded alternation-heavy explicit-empty-else conditional workflows supported by `RBR-0128` produce real `rebar` timings before replacement-conditioned work or broader backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_empty_else_boundary` manifest and converts its explicit alternation-heavy gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0128`, such as `a(b)?c(?(1)(de|df)|)` and `a(?P<word>b)?c(?(word)(de|df)|)`, through module and compiled-`Pattern` entrypoints with representative present-arm and absent-else haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported explicit-empty-else alternation-heavy workflows while leaving replacement-conditioned helpers, wider conditional-arm alternation, quantified conditionals, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0128`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0128`.
- This task exists so the first bounded backtracking-heavy conditional slice is measured on the same benchmark surface that previously carried it only as an explicit gap row.
