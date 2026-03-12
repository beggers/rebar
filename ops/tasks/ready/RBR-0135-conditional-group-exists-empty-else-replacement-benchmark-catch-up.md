# RBR-0135: Catch bounded explicit-empty-else conditional replacement benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded explicit-empty-else conditional replacement workflows supported by `RBR-0134` produce real `rebar` timings before empty-yes-arm replacement, nested conditionals, quantified conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing explicit-empty-else conditional manifest to exercise only the bounded replacement workflows already supported by `RBR-0134`, such as `a(b)?c(?(1)d|)` and `a(?P<word>b)?c(?(word)d|)` through module and compiled-`Pattern` `sub()` or `subn()` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported explicit-empty-else conditional replacement workflows while leaving empty-yes-arm or fully-empty conditional replacement helpers, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0134`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0112` and `RBR-0134`.
- Use the existing `module-sub-numbered-conditional-group-exists-empty-else-replacement-warm-gap` row in `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded explicit-empty-else conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.
