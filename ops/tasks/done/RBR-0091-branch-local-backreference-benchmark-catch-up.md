# RBR-0091: Catch branch-local backreference benchmarks up with the new bounded slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded branch-local backreference workflows supported by `RBR-0090` produce real `rebar` timings before quantified branches or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/branch_local_backreference_boundary.json`
- `tests/benchmarks/test_branch_local_backreference_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated branch-local backreference manifest that exercises only the bounded workflows already supported by `RBR-0090`, such as `a((b)|c)\\2d` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)d` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported branch-local backreference workflows while leaving broader quantified-branch, conditional, nested-alternation, or backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0090`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0090`.
- This task exists so the queue does not reach bounded branch-local backreference parity and then leave that newly supported slice absent from benchmark reporting.
- Completed 2026-03-12: added `branch_local_backreference_boundary.json`, covered the combined benchmark publication with a dedicated regression test, and republished `reports/benchmarks/latest.json` at 147 total workloads with 119 measured timings and 28 explicit known gaps.
