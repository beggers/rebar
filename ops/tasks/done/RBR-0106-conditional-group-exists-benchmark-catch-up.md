# RBR-0106: Catch bounded conditional group-exists benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded conditional group-exists workflows supported by `RBR-0105` produce real `rebar` timings before assertion-conditioned branches or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated conditional manifest that exercises only the bounded workflows already supported by `RBR-0105`, such as `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` through module and compiled-`Pattern` entrypoints, including representative group-present and group-omitted haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported conditional workflows while leaving assertion-conditioned branches, nested conditionals, conditional replacement behavior, quantified conditionals, or broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0105`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0105`.
- This task exists so the queue does not reach bounded conditional parity and then leave that newly supported slice absent from benchmark reporting.
- Completed 2026-03-12: added the dedicated `conditional-group-exists-boundary` benchmark manifest, wired it into the default benchmark suite, added regression coverage for the combined scorecard, and republished `reports/benchmarks/latest.json` at 186 workloads with 149 measured timings and 37 explicit gaps.
