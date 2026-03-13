# RBR-0206: Catch bounded conditional-plus-branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded conditional-plus-branch-local-backreference workflows supported by `RBR-0205` produce real `rebar` timings before broader backtracking-heavy conditional or grouped execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/branch_local_backreference_boundary.json`
- `tests/benchmarks/test_branch_local_backreference_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `branch_local_backreference_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0205`, anchored by the existing named `pattern.fullmatch` conditional gap row for `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)` and any directly adjacent numbered or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported conditional-plus-branch-local-backreference workflows while leaving quantified branches, replacement semantics, nested conditionals, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0205`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0205`.
- Keep this slice in the existing `branch_local_backreference_boundary` manifest rather than inventing a second benchmark family for the same combined branch-local/conditional surface.
- This task exists so the queue does not reach bounded conditional-plus-branch-local-backreference parity and then leave that newly supported slice absent from benchmark reporting.
