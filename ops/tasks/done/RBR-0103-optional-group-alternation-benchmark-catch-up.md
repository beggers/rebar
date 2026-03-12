# RBR-0103: Catch optional-group alternation benchmarks up with the new bounded slice

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded optional-group alternation workflows supported by `RBR-0102` produce real `rebar` timings before conditionals or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/optional_group_alternation_boundary.json`
- `tests/benchmarks/test_optional_group_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated optional-group alternation manifest that exercises only the bounded workflows already supported by `RBR-0102`, such as `a(b|c)?d` and `a(?P<word>b|c)?d` through module and compiled-`Pattern` entrypoints, including representative branch-present and group-omitted haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported optional-group alternation workflows while leaving exact or ranged quantified alternation, branch-local backreferences inside quantified alternation, conditional, or broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0102`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0102`.
- This task exists so the queue does not reach bounded optional-group alternation parity and then leave that newly supported quantified-alternation slice absent from benchmark reporting.
- Completed with a dedicated `optional-group-alternation-boundary` benchmark manifest, updated optional-group benchmark expectations after moving the old quantified-alternation placeholder out of the plain optional-group pack, a new combined benchmark regression test for the current frontier, and a republished `reports/benchmarks/latest.json` at 178 workloads with 143 measured timings and 35 explicit gaps.
