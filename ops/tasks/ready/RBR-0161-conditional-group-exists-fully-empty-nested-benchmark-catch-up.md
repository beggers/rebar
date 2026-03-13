# RBR-0161: Catch bounded nested fully-empty conditional benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded nested fully-empty conditional workflows supported by `RBR-0160` produce real `rebar` timings before broader nested empty-arm or backtracking-heavy conditionals reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness reuses the existing `conditional_group_exists_fully_empty_boundary` manifest and converts its explicit nested-conditional gap row into real measured `rebar` workloads for the bounded workflows already supported by `RBR-0160`, such as `a(b)?c(?(1)|(?(1)|))` and `a(?P<word>b)?c(?(word)|(?(word)|))`, through module and compiled-`Pattern` entrypoints with representative capture-present and capture-absent haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested fully-empty conditional workflows while leaving replacement-conditioned helpers, deeper nesting, quantified conditionals, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0160`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0160`.
- Use the corrected `module-search-numbered-nested-conditional-group-exists-fully-empty-cold-gap` row in `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded nested fully-empty parity and then leave that newly supported slice absent from benchmark reporting.
