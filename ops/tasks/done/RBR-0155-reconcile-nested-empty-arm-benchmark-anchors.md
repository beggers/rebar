# RBR-0155: Reconcile the nested empty-arm benchmark anchors

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Correct the published benchmark manifest contracts so the nested empty-yes-arm and nested fully-empty known-gap rows point at distinct CPython-accepted patterns instead of collapsing to the same stored pattern.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_yes_else_boundary_benchmarks.py`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The nested empty-yes-arm benchmark anchor remains pinned to `module-search-numbered-nested-conditional-group-exists-empty-yes-else-cold-gap` for `a(b)?c(?(1)|(?(1)e|f))`, and the manifest text stays clear that this row represents the bounded nested empty-yes-arm follow-on rather than a broader empty-arm bucket.
- The nested fully-empty benchmark anchor in `conditional_group_exists_fully_empty_boundary.json` is corrected to a distinct CPython-accepted nested fully-empty pattern, such as `a(b)?c(?(1)|(?(1)|))`, instead of reusing the empty-yes-arm pattern.
- The benchmark tests and republished combined scorecard reflect the corrected manifest contracts without silently dropping workloads or changing the adapter/provenance reporting model.
- This task is harness/reporting cleanup only. It must not broaden regex execution support, silently delegate new runtime behavior to stdlib `re`, or change the benchmark schema.

## Constraints
- Keep the workload counts stable unless a manifest bug fix makes a count change unavoidable; if a count changes, update the tests and completion note to explain exactly why.
- Reuse the existing benchmark runner and combined-scorecard contract for `reports/benchmarks/latest.json`.
- Do not turn this into the runtime implementation task for nested empty-arm behavior.

## Notes
- This task unblocks post-`RBR-0154` queue growth by turning the ambiguous nested empty-arm gap rows into distinct worker contracts.
- Build on `RBR-0150` and the current conditional benchmark manifests.

## Completion Note
- Corrected the nested fully-empty benchmark anchor to `a(b)?c(?(1)|(?(1)|))` with a matching `zzaczz` haystack, kept the nested empty-yes-arm anchor pinned to `a(b)?c(?(1)|(?(1)e|f))`, regenerated `reports/benchmarks/latest.json`, and tightened both targeted benchmark tests to assert the distinct anchor patterns explicitly.
- Published workload counts stayed stable in the tracked benchmark report (`293` total / `239` measured / `54` known gaps). The two targeted benchmark tests also needed stale combined-suite totals refreshed to the current manifest sets; that was test maintenance only, not a benchmark-schema or workload-count change in the published report.
