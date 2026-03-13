# RBR-0242: Catch bounded wider ranged-repeat quantified-group alternation plus conditional benchmarks up with the new slice

Status: done
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

## Completion
- Promoted the existing wider ranged-repeat grouped-conditional benchmark anchor into measured coverage and added the minimal numbered and named compile/module/pattern companion rows in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`.
- Refreshed the combined benchmark assertions, including the adjacent carried-forward bounded conditional anchor in `benchmarks/workloads/open_ended_quantified_group_boundary.json`, so the published report stays honest now that the shared bounded `a((bc|de){1,3})?(?(1)d|e)` slice benchmarks successfully in both manifests.
- Republished `reports/benchmarks/latest.json`; the combined scorecard now reports 420 workloads across 30 manifests with 384 real `rebar` timings and 36 explicit known gaps, while the wider ranged-repeat quantified-group manifest now reports 16 workloads with 13 measured rows and 3 remaining gaps.
