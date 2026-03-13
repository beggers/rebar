# RBR-0180: Catch bounded quantified explicit-empty-else conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified explicit-empty-else conditional workflows supported by `RBR-0179` produce real `rebar` timings once the accepted repeated `|)` spelling has real Rust-backed parity.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_empty_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_empty_else_boundary` manifest to exercise only the bounded quantified explicit-empty-else workflows already supported by `RBR-0179`, anchored by the current `pattern-fullmatch-numbered-quantified-conditional-group-exists-empty-else-purged-gap` row and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified explicit-empty-else workflows, such as `a(b)?c(?(1)d|){2}` and `a(?P<word>b)?c(?(word)d|){2}`, while leaving omitted-no-arm or empty-arm quantified variants, replacement-conditioned helpers, alternation-heavy repeated arms, nested quantified conditionals, ranged/open-ended repeats, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0179`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0179`.
- Use the existing `pattern-fullmatch-numbered-quantified-conditional-group-exists-empty-else-purged-gap` row in `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach quantified explicit-empty-else parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added representative numbered and named quantified explicit-empty-else benchmark rows around the existing anchor so the manifest now publishes real `rebar` timings for `a(b)?c(?(1)d|){2}` and `a(?P<word>b)?c(?(word)d|){2}` through module-search and Pattern.fullmatch probes.
- Regenerated `reports/benchmarks/latest.json`; the combined benchmark scorecard now reports 315 workloads, 269 measured `rebar` timings, and 46 known gaps.
- Verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_conditional_group_exists_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_empty_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_no_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_empty_yes_else_boundary_benchmarks tests.benchmarks.test_conditional_group_exists_fully_empty_boundary_benchmarks tests.benchmarks.test_quantified_alternation_boundary_benchmarks tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks`.
