# RBR-0227: Catch bounded broader-range quantified-alternation benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded broader-range quantified-alternation workflows supported by `RBR-0226` produce real `rebar` timings before open-ended repeats or broader repeated-backtracking execution reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0226`, anchored by the existing numbered `module.search` broader-range gap row for `a(b|c){1,3}d` and any directly adjacent compile, pattern, or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported broader-range quantified-alternation workflows while leaving open-ended repeats, nested alternation, branch-local backreferences, conditional combinations, and broader repeated-backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0226`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0226`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded broader-range quantified-alternation surface.
- This task exists so the queue does not reach bounded broader-range quantified-alternation parity and then leave that newly supported slice absent from benchmark reporting.
