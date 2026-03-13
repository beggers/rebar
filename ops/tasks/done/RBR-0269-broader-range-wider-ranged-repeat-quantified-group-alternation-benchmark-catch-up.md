# RBR-0269: Catch broader-range wider-ranged-repeat quantified-group alternation benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the broader `{1,4}` grouped-alternation workflows supported by `RBR-0268` produce real `rebar` timings without leaving the newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a(bc|de){1,4}d` and `a(?P<word>bc|de){1,4}d` workflows while leaving grouped conditionals, grouped backtracking-heavy flows, replacement semantics, and broader grouped execution explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0268`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0268`.
- Reuse the existing `module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap` anchor instead of forking another manifest.
- Keep the benchmark slice narrow and sequential so grouped-conditionals or broader grouped backtracking do not reopen before this Python-path catch-up lands.

## Completion
- Promoted the existing broader-range numbered anchor into a measured workload and added the adjacent numbered/named compile and `Pattern.fullmatch()` companion rows needed to publish the bounded `{1,4}` grouped-alternation benchmark slice cleanly.
- Updated the focused wider-ranged-repeat benchmark test plus combined source-tree benchmark expectations, and republished `reports/benchmarks/latest.json` with the wider-ranged-repeat manifest at 30 measured workloads, the combined suite at 430 measured workloads, and 31 explicit known gaps still covering later grouped follow-ons.
