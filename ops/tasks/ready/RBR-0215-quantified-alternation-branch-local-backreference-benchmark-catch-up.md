# RBR-0215: Catch bounded quantified-alternation-plus-branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified-alternation-plus-branch-local-backreference workflows supported by `RBR-0214` produce real `rebar` timings before broader counted-repeat backtracking-heavy grouped execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0214`, anchored by the existing numbered `module.search` branch-backreference gap row for `a((b|c)\\2){1,2}d` and any directly adjacent named or compiled-`Pattern` companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-alternation-plus-branch-local-backreference workflows while leaving broader counted ranges, open-ended repeats, replacement semantics, conditional combinations, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0214`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0214`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded quantified-alternation-plus-branch-local-backreference surface.
- This task exists so the queue does not reach bounded quantified-alternation-plus-branch-local-backreference parity and then leave that newly supported slice absent from benchmark reporting.
