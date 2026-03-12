# RBR-0112: Catch bounded conditional explicit-empty-else benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded explicit-empty-else conditional group-exists workflows supported by `RBR-0111` produce real `rebar` timings before rejected-syntax diagnostics or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated conditional manifest that exercises only the bounded explicit-empty-else workflows already supported by `RBR-0111`, such as `a(b)?c(?(1)d|)` and `a(?P<word>b)?c(?(word)d|)` through module and compiled-`Pattern` entrypoints, including representative group-present and group-omitted haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported explicit-empty-else conditional workflows while leaving assertion-conditioned branches, nested conditionals, conditional replacement behavior, quantified conditionals, or broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0111`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0111`.
- This task exists so the queue does not reach bounded explicit-empty-else conditional parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- 2026-03-12: Added `conditional_group_exists_empty_else_boundary.json`, wired it into the default benchmark manifest set, added dedicated combined-scorecard coverage in `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`, refreshed the adjacent omitted-no-arm benchmark expectations now that the carry-forward explicit-empty-else row measures after `RBR-0111`, and regenerated `reports/benchmarks/latest.json` to publish the new 208-workload / 162-measured / 46-gap combined benchmark surface.
