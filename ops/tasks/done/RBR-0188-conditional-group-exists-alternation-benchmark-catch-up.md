# RBR-0188: Catch bounded alternation-heavy two-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded alternation-heavy two-arm conditional workflows supported by `RBR-0187` produce real `rebar` timings as soon as the first broader backtracking-heavy conditional slice lands.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded alternation-heavy two-arm conditional workflows already supported by `RBR-0187`, anchored by a new numbered `module.search` row for `a(b)?c(?(1)(de|df)|(eg|eh))` and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported alternation-heavy two-arm conditional workflows while leaving broader alternation-heavy conditionals, quantified repeats, replacement-conditioned helpers, deeper nested conditionals, branch-local backreferences inside the alternations, and broader backtracking-heavy shapes as explicit known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0187`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current honest-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0187`.
- Keep this slice in the existing `conditional_group_exists_boundary` manifest rather than inventing a second benchmark family for the same bounded two-arm conditional surface.
- This task exists so the queue does not widen into the first broader conditional slice and then leave that newly supported behavior missing from benchmark reporting.

## Completion Notes
- Added four measured alternation-heavy two-arm conditional benchmark rows to `benchmarks/workloads/conditional_group_exists_boundary.json`: a numbered `module.search` anchor plus named `module.search` and numbered/named `Pattern.fullmatch()` companions for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`.
- Updated `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py` to assert the expanded 16-row manifest and the regenerated combined-suite totals of 322 workloads, 277 measured workloads, and 45 known gaps.
- Republished `reports/benchmarks/latest.json` and verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_conditional_group_exists_boundary_benchmarks`.
