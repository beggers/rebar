# RBR-0194: Catch bounded two-arm conditional replacement benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded two-arm conditional replacement workflows supported by `RBR-0193` produce real `rebar` timings before alternation-heavy replacement branches, nested replacement-conditioned flows, quantified replacement-conditioned conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded replacement workflows already supported by `RBR-0193`, such as `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` through module and compiled-`Pattern` `sub()` or `subn()` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported two-arm conditional replacement workflows while leaving replacement templates that read captures, callable replacements, alternation-heavy replacement branches, nested conditionals, quantified conditionals, and broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0193`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0193`.
- Keep this slice in the existing `conditional_group_exists_boundary` manifest rather than inventing a second benchmark family for the same bounded two-arm conditional surface.
- This task exists so the queue does not reach bounded two-arm conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.
