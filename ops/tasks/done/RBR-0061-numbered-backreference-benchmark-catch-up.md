# RBR-0061: Catch numbered-backreference benchmarks up with the new grouped-reference slice

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded numbered-backreference workflows supported by `RBR-0060` produce real `rebar` timings instead of leaving benchmark reporting behind the grouped-reference correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/numbered_backreference_boundary.json`
- `tests/benchmarks/test_numbered_backreference_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated numbered-backreference manifest that exercises only the bounded literal workflows already supported by `RBR-0060`, such as `(ab)\\1` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported numbered-backreference workflows while leaving any still-unsupported grouped-reference shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0060`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0058` and `RBR-0060`.
- This task exists so the queue does not reach numbered-backreference parity and then leave that newly supported surface absent from benchmark reporting.

## Completion Note
- Added `benchmarks/workloads/numbered_backreference_boundary.json` with three measured bounded `(ab)\1` workloads plus two explicit grouped-segment known-gap rows.
- Wired the new manifest into the default combined benchmark suite in `python/rebar_harness/benchmarks.py` and regenerated `reports/benchmarks/latest.json`, moving the published benchmark scorecard to 63 workloads with 50 measured timings and 13 known gaps.
- Added `tests/benchmarks/test_numbered_backreference_boundary_benchmarks.py` to lock the combined-suite counts plus the new manifest's measured-versus-gap behavior and smoke workload IDs.
