# RBR-0174: Catch bounded alternation-bearing fully-empty conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded alternation-bearing fully-empty conditional workflows supported by `RBR-0173` produce real `rebar` timings once the corrected fully-empty benchmark anchor is distinct from the empty-yes-arm spelling.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_fully_empty_boundary` manifest and converts its explicit alternation-heavy gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0173`, such as `a(b)?c(?(1)|(?:|))` and `a(?P<word>b)?c(?(word)|(?:|))`, through module and compiled-`Pattern` entrypoints with representative capture-present and capture-absent haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported fully-empty alternation-bearing workflows while leaving quantified follow-ons, replacement-conditioned helpers, nested alternation-bearing conditionals, wider alternation-heavy arms, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0173`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0173`.
- Use the corrected `module-search-numbered-conditional-group-exists-fully-empty-alternation-heavy-warm-gap` row in `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded fully-empty alternation parity and then leave that accepted syntax slice absent from benchmark reporting.

## Completion
- Converted the anchored alternation-bearing fully-empty gap row into four measured module-search and `Pattern.fullmatch()` workloads covering numbered and named forms across representative capture-absent and capture-present haystacks.
- Updated the focused manifest regression test and regenerated `reports/benchmarks/latest.json`; the combined benchmark report now publishes 309 workloads with 261 measured `rebar` timings and 48 explicit known gaps, while `conditional-group-exists-fully-empty-boundary` is fully measured at 24/24 workloads.
