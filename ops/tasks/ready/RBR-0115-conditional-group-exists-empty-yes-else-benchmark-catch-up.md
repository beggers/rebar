# RBR-0115: Catch bounded conditional empty-yes-arm benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded empty-yes-arm conditional group-exists workflows supported by `RBR-0114` produce real `rebar` timings before rejected-syntax diagnostics or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_yes_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated conditional manifest that exercises only the bounded empty-yes-arm workflows already supported by `RBR-0114`, such as `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)` through module and compiled-`Pattern` entrypoints, including representative group-present and group-omitted haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported empty-yes-arm conditional workflows while leaving fully empty `(?(1)|)` / `(?(name)|)` forms, assertion-conditioned branches, nested conditionals, conditional replacement behavior, quantified conditionals, or broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0114`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0114`.
- This task exists so the queue does not reach bounded empty-yes-arm conditional parity and then leave that newly supported slice absent from benchmark reporting.
