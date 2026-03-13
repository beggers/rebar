# RBR-0171: Catch bounded alternation-heavy empty-yes-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded alternation-heavy empty-yes-arm conditional workflows supported by `RBR-0170` produce real `rebar` timings before the fully-empty alternation-bearing follow-on or any broader backtracking-heavy empty-arm work reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_yes_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_empty_yes_else_boundary` manifest and converts its explicit alternation-heavy gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0170`, such as `a(b)?c(?(1)|(e|f))` and `a(?P<word>b)?c(?(word)|(e|f))`, through module and compiled-`Pattern` entrypoints with representative present-arm and absent-arm haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported empty-yes-arm alternation-heavy workflows while leaving replacement-conditioned helpers, quantified and nested follow-ons, wider alternation-heavy arms, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0170`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0170`.
- Use the existing `module-search-numbered-conditional-group-exists-empty-yes-else-alternation-heavy-warm-gap` row in `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded empty-yes-arm alternation parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Converted the anchored alternation-heavy empty-yes-arm gap row into four measured module-search and `Pattern.fullmatch()` workloads covering numbered and named forms across representative present-arm and absent-arm haystacks.
- Updated the manifest regression test and regenerated `reports/benchmarks/latest.json`; the combined benchmark report now publishes 306 workloads with 257 measured `rebar` timings and 49 explicit known gaps, while `conditional-group-exists-empty-yes-else-boundary` is fully measured at 27/27 workloads.
