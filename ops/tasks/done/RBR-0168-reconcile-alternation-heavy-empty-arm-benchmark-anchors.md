# RBR-0168: Reconcile the alternation-heavy empty-arm benchmark anchors

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Correct the published benchmark manifest contracts so the alternation-heavy empty-yes-arm and fully-empty known-gap rows point at distinct CPython-accepted patterns instead of collapsing to the same stored pattern.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_yes_else_boundary_benchmarks.py`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The alternation-heavy empty-yes-arm benchmark anchor remains pinned to `module-search-numbered-conditional-group-exists-empty-yes-else-alternation-heavy-warm-gap` for `a(b)?c(?(1)|(e|f))`, and the manifest text stays clear that this row represents the broader empty-yes-arm alternation follow-on rather than a generic backtracking bucket.
- The alternation-heavy fully-empty benchmark anchor in `conditional_group_exists_fully_empty_boundary.json` is corrected to a distinct CPython-accepted alternation-bearing fully-empty pattern, such as `a(b)?c(?(1)|(?:|))`, instead of reusing the empty-yes-arm pattern.
- The targeted benchmark tests and the republished combined scorecard reflect the corrected manifest contracts without silently dropping workloads or changing the adapter/provenance reporting model.
- This task is harness/reporting cleanup only. It must not broaden regex execution support, silently delegate new runtime behavior to stdlib `re`, or change the benchmark schema.

## Constraints
- Keep the workload counts stable unless a manifest bug fix makes a count change unavoidable; if a count changes, update the tests and completion note to explain exactly why.
- Reuse the existing benchmark runner and combined-scorecard contract for `reports/benchmarks/latest.json`.
- Do not turn this into the runtime implementation task for alternation-heavy empty-arm behavior.

## Notes
- Build on `RBR-0167` and `RBR-0155`.
- This task exists so the queue can reopen broader alternation-heavy empty-yes-arm and fully-empty slices with distinct worker contracts instead of two ambiguous gap rows.
- Completed 2026-03-13: kept the empty-yes-arm benchmark anchor pinned to `a(b)?c(?(1)|(e|f))`, corrected the fully-empty alternation-heavy benchmark anchor to `a(b)?c(?(1)|(?:|))`, tightened the two benchmark tests to assert the exact patterns and explanatory notes, and republished `reports/benchmarks/latest.json` with stable 303-workload / 253-measured / 50-gap totals.
