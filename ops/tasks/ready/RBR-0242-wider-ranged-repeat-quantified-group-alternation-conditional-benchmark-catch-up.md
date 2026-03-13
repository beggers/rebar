# RBR-0242: Catch bounded wider ranged-repeat quantified-group alternation plus conditional benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded grouped-alternation-plus-conditional `{1,3}` workflows supported by `RBR-0241` produce real `rebar` timings before broader grouped backtracking or open-ended grouped-conditionals reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `module-search-numbered-wider-ranged-repeat-group-conditional-warm-gap` anchor into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported wider ranged-repeat grouped-alternation-plus-conditional workflows while leaving open-ended grouped-conditionals, broader counted ranges, replacement semantics, and broader grouped backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0241`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0241`.
- Reuse the existing `module-search-numbered-wider-ranged-repeat-group-conditional-warm-gap` row as the benchmark anchor instead of forking another manifest.
- This task exists so the queue does not reach grouped-alternation-plus-conditional parity and then leave that newly supported slice absent from benchmark reporting.
