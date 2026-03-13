# RBR-0177: Catch bounded quantified omitted-no-arm conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified omitted-no-arm conditional workflows supported by `RBR-0176` produce real `rebar` timings before quantified explicit-empty-else follow-ons or broader backtracking-heavy conditional execution reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_no_else_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_no_else_boundary` manifest to exercise only the bounded quantified omitted-no-arm workflows already supported by `RBR-0176`, anchored by the current `pattern-fullmatch-numbered-quantified-conditional-group-exists-no-else-purged-gap` row and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified omitted-no-arm workflows, such as `a(b)?c(?(1)d){2}` and `a(?P<word>b)?c(?(word)d){2}`, while leaving explicit-empty-else or empty-arm quantified variants, replacement-conditioned helpers, alternation-heavy repeated arms, nested quantified conditionals, ranged/open-ended repeats, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0176`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0176`.
- Use the existing `pattern-fullmatch-numbered-quantified-conditional-group-exists-no-else-purged-gap` row in `benchmarks/workloads/conditional_group_exists_no_else_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach quantified omitted-no-arm parity and then leave that newly supported slice absent from benchmark reporting.

## Completion Notes
- Completed 2026-03-13.
- Extended `benchmarks/workloads/conditional_group_exists_no_else_boundary.json` so the existing numbered quantified anchor now measures real timings and the manifest also covers numbered and named module-search plus named `Pattern.fullmatch()` companion rows for the bounded `{2}` omitted-no-arm slice.
- Updated `tests/benchmarks/test_conditional_group_exists_no_else_boundary_benchmarks.py` to validate the published 29-manifest combined-suite totals and the now-measured quantified omitted-no-arm workloads.
- Republished `reports/benchmarks/latest.json`; the combined scorecard now reports 312 workloads with 265 real `rebar` timings and 47 explicit known gaps, while the `conditional-group-exists-no-else-boundary` manifest now reports 27 workloads with 27 measured rows and 0 remaining known gaps.
