# RBR-0138: Catch bounded empty-yes-arm conditional replacement benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded empty-yes-arm conditional replacement workflows supported by `RBR-0137` produce real `rebar` timings before fully-empty replacement, nested conditionals, quantified conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_yes_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing empty-yes-arm conditional manifest to exercise only the bounded replacement workflows already supported by `RBR-0137`, such as `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)` through module and compiled-`Pattern` `sub()` or `subn()` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported empty-yes-arm conditional replacement workflows while leaving fully-empty conditional replacement helpers, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0137`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0115` and `RBR-0137`.
- Use the existing `module-sub-numbered-conditional-group-exists-empty-yes-else-replacement-warm-gap` row in `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded empty-yes-arm conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.
