# RBR-0183: Catch bounded nested two-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded nested two-arm conditional workflows supported by `RBR-0182` produce real `rebar` timings and eliminate the remaining `conditional_group_exists_boundary` gap row.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded nested two-arm conditional workflows already supported by `RBR-0182`, anchored by the current `module-search-numbered-nested-conditional-group-exists-cold-gap` row and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported nested two-arm conditional workflows while leaving broader nested, quantified, replacement-conditioned, or backtracking-heavy conditional shapes as explicit gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0182`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current honest-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0182`.
- Use the existing `module-search-numbered-nested-conditional-group-exists-cold-gap` row in `benchmarks/workloads/conditional_group_exists_boundary.json` as the benchmark anchor for this slice.
- This task exists so the last currently queued `conditional_group_exists_boundary` gap reaches the published benchmark surface before the queue moves on to broader backtracking-heavy conditional execution.

## Completion
- Replaced the lingering nested two-arm gap row in `conditional_group_exists_boundary.json` with four measured numbered/named nested search and `Pattern.fullmatch()` workloads matching the bounded `RBR-0182` slice.
- Regenerated `reports/benchmarks/latest.json`; the combined benchmark report now publishes 318 workloads with 273 real `rebar` timings and 45 explicit known gaps, and `conditional-group-exists-boundary` is now fully measured at 12 of 12 workloads.
- Verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_conditional_group_exists_boundary_benchmarks`.
