# RBR-0132: Catch bounded conditional no-else replacement benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded omitted-no-arm conditional replacement workflows supported by `RBR-0131` produce real `rebar` timings before nested conditionals, quantified conditionals, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_no_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing omitted-no-arm conditional manifest to exercise only the bounded replacement workflows already supported by `RBR-0131`, such as `a(b)?c(?(1)d)` and `a(?P<word>b)?c(?(word)d)` through module and compiled-`Pattern` `sub()` or `subn()` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported omitted-no-arm conditional replacement workflows while leaving explicit-empty-else, empty-yes-arm, fully-empty, nested-conditional, quantified-conditional, alternation-heavy conditional-arm, or broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0131`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0109` and `RBR-0131`.
- Use the existing `module-sub-numbered-conditional-group-exists-no-else-replacement-warm-gap` row in `benchmarks/workloads/conditional_group_exists_no_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach bounded omitted-no-arm conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added bounded numbered and named omitted-no-arm conditional replacement benchmark rows for module and compiled-`Pattern` `sub()`/`subn()` entrypoints while leaving nested, quantified, and alternation-heavy conditional shapes as explicit gaps.
- Regenerated `reports/benchmarks/latest.json`; the published benchmark report now records 262 total workloads with 201 measured `rebar` timings and 61 known gaps.
