# RBR-0191: Catch bounded quantified alternation-heavy two-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified alternation-heavy two-arm conditional workflows supported by `RBR-0190` produce real `rebar` timings as soon as that exact quantified follow-on lands.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded quantified alternation-heavy two-arm conditional workflows already supported by `RBR-0190`, anchored by a new numbered `Pattern.fullmatch()` row for `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported quantified alternation-heavy two-arm conditional workflows while leaving broader quantified alternation-heavy conditionals, replacement-conditioned helpers, deeper nested conditionals, branch-local backreferences inside the alternations, ranged/open-ended repeats, and broader backtracking-heavy shapes as explicit known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0190`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current honest-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0190`.
- Keep this slice in the existing `conditional_group_exists_boundary` manifest rather than inventing a second benchmark family for the same bounded two-arm conditional surface.
- This task exists so the queue does not widen into the quantified follow-on and then leave that newly supported behavior missing from benchmark reporting.

## Completion Note
- Repointed the four alternation-heavy measured rows in `conditional_group_exists_boundary.json` to the bounded quantified alternation-heavy two-arm conditional slice from `RBR-0190`, regenerated `reports/benchmarks/latest.json` with the same `322` total / `277` measured / `45` known-gap contract, and updated the benchmark assertion coverage to the new quantified patterns and haystacks.
