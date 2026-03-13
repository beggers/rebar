# RBR-0144: Catch bounded alternation-heavy omitted-no-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded alternation-heavy omitted-no-arm conditional workflows supported by `RBR-0143` produce real `rebar` timings before nested conditionals, quantified conditionals, or broader backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_no_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_no_else_boundary` manifest and converts its explicit alternation-heavy gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0143`, such as `a(b)?c(?(1)(de|df))` and `a(?P<word>b)?c(?(word)(de|df))`, through module and compiled-`Pattern` entrypoints with representative first-arm, second-arm, and absent-no-match haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported omitted-no-arm alternation-heavy workflows while leaving replacement-conditioned helpers, empty-arm variants, nested conditionals, quantified conditionals, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0143`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0143`.
- Use the existing `module-search-numbered-conditional-group-exists-no-else-alternation-heavy-warm-gap` row in `benchmarks/workloads/conditional_group_exists_no_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded omitted-no-arm alternation-heavy parity and then leave that newly supported slice absent from benchmark reporting.

## Completion Notes
- Completed 2026-03-13.
- Extended `benchmarks/workloads/conditional_group_exists_no_else_boundary.json` so the existing numbered alternation-heavy anchor row now measures real timings and the manifest also covers the named first-arm module path plus numbered and named compiled-`Pattern` absent no-match probes.
- Updated `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py` to validate the current 29-manifest combined suite totals and the new measured alternation-heavy omitted-no-arm workloads.
- Republished `reports/benchmarks/latest.json`; the combined scorecard now reports 286 workloads with 229 real `rebar` timings and 57 explicit known gaps, while the `conditional-group-exists-no-else-boundary` manifest now reports 21 workloads with 19 measured rows and 2 remaining known gaps.
