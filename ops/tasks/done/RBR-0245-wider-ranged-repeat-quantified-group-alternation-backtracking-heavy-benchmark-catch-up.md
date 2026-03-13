# RBR-0245: Catch bounded wider ranged-repeat quantified-group alternation backtracking-heavy benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded grouped backtracking-heavy `{1,3}` workflows supported by `RBR-0244` produce real `rebar` timings before open-ended grouped-conditionals reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-backtracking-heavy-purged-gap` anchor into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported wider ranged-repeat grouped backtracking-heavy workflows while leaving open-ended grouped-conditionals, broader counted ranges, replacement semantics, and broader grouped backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0244`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0244`.
- Reuse the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-backtracking-heavy-purged-gap` row as the benchmark anchor instead of forking another manifest.
- This task exists so the queue does not reach grouped backtracking-heavy parity and then leave that newly supported slice absent from benchmark reporting.
- Completed with six measured bounded `{1,3}` grouped backtracking-heavy rows: numbered and named `module.compile`, `module.search`, and `pattern.fullmatch` coverage now publishes real `rebar` timings in `reports/benchmarks/latest.json`.
- Corrected the future `pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap` placeholder to the real `{1,}` pattern so the open-ended follow-on stays an honest known gap for `RBR-0251`.
