# RBR-0212: Catch bounded optional-group-alternation-plus-branch-local-backreference benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded optional-group-alternation-plus-branch-local-backreference workflows supported by `RBR-0211` produce real `rebar` timings before broader counted-repeat quantified-alternation-plus-backreference work reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/optional_group_alternation_boundary.json`
- `tests/benchmarks/test_optional_group_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `optional_group_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0211`, anchored by the existing numbered `pattern.fullmatch` branch-backreference gap row for `a((b|c)\\2)?d` and any directly adjacent named or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported optional-group-alternation-plus-branch-local-backreference workflows while leaving broader counted repeats, quantified alternation plus backreferences, replacement semantics, conditional combinations, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0211`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0211`.
- Keep this slice in the existing `optional_group_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded optional-group-alternation-plus-branch-local-backreference surface.
- This task exists so the queue does not reach bounded optional-group-alternation-plus-branch-local-backreference parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added numbered and named compile/search/fullmatch benchmark rows for `a((b|c)\\2)?d` and `a(?P<outer>(?P<inner>b|c)(?P=inner))?d` in `benchmarks/workloads/optional_group_alternation_boundary.json`, reusing the existing numbered `pattern.fullmatch` anchor and leaving the broader counted-repeat alternation row as the remaining explicit gap.
- Regenerated `reports/benchmarks/latest.json`; the published report now records 371 total workloads, 327 measured `rebar` timings, and 44 explicit known gaps, with the optional-group alternation manifest at 13 workloads / 12 measured / 1 gap.
- Verified with `python3 -m unittest -q tests.benchmarks.test_optional_group_alternation_boundary_benchmarks tests.benchmarks.test_quantified_alternation_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_no_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_empty_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_empty_yes_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_fully_empty_boundary_benchmarks`.
