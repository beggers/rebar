# RBR-0209: Catch bounded quantified branch-local-backreference benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified branch-local-backreference workflows supported by `RBR-0208` produce real `rebar` timings before broader backtracking-heavy grouped execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/branch_local_backreference_boundary.json`
- `tests/benchmarks/test_branch_local_backreference_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `branch_local_backreference_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0208`, anchored by the existing numbered `module.search` quantified gap row for `a((b)+|c)\\2d` and any directly adjacent named or compiled-`Pattern` companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified branch-local-backreference workflows while leaving conditional combinations, replacement semantics, nested alternations, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0208`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0208`.
- Keep this slice in the existing `branch_local_backreference_boundary` manifest rather than inventing a second benchmark family for the same quantified branch-local surface.
- This task exists so the queue does not reach bounded quantified branch-local-backreference parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added numbered and named quantified branch-local-backreference compile/search/fullmatch benchmark rows to the existing `branch_local_backreference_boundary` manifest, reusing the existing numbered `module.search` anchor row instead of introducing a new benchmark family.
- Regenerated `reports/benchmarks/latest.json`, moving the published benchmark surface to 366 workloads with 321 measured `rebar` timings and 45 explicit known gaps.
