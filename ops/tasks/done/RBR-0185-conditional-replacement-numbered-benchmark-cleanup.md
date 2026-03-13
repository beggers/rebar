# RBR-0185: Retire the remaining numbered conditional replacement benchmark-only gaps

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the remaining numbered `module.sub()` conditional-replacement benchmark-only rows into real `rebar` timings so the published benchmark surface sheds obvious debt before broader backtracking-heavy conditional execution reopens.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_no_else_boundary.json`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness converts the three remaining numbered replacement gap rows into real timings without changing benchmark schema or broadening regex support:
  - `module-sub-numbered-conditional-group-exists-no-else-replacement-warm-gap`
  - `module-sub-numbered-conditional-group-exists-empty-else-replacement-warm-gap`
  - `module-sub-numbered-conditional-group-exists-fully-empty-replacement-warm-gap`
- `reports/benchmarks/latest.json` records real `rebar` timings for those numbered `module.sub()` helper paths while preserving the existing measured rows for `subn()` and compiled-`Pattern` replacement helpers in the same manifests.
- The updated manifests keep explicit cache-mode and adapter-provenance reporting and leave unrelated unsupported behaviors as honest known gaps instead of silently omitting them.
- The task does not change `reports/benchmarks/native_smoke.json`, does not claim built-native full-suite publication, and does not add new regex semantics beyond behavior already supported through the Rust boundary.

## Constraints
- Keep this task scoped to benchmark catch-up for already-supported numbered conditional replacement workflows; do not broaden into new correctness publication, new runtime behavior, nested/quantified/backtracking-heavy conditionals, or stdlib delegation.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding replacement workflow is supposed to run through `rebar._rebar`.

## Notes
- Build on `RBR-0184`, `RBR-0132`, `RBR-0135`, and `RBR-0141`.
- This task exists because the current benchmark report still carries three obvious numbered replacement gap rows even though the corresponding conditional replacement behavior already exists behind the Rust boundary.
- 2026-03-13: Confirmed the three numbered `module.sub()` replacement rows now publish real `rebar` timings in `reports/benchmarks/latest.json`; updated the three conditional benchmark suite tests to the current 318-workload, 273-measured, 45-gap full-suite totals so the queue state matches the landed publication.
