# RBR-0266: Catch nested open-ended quantified-group alternation benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the nested open-ended grouped-alternation workflows supported by `RBR-0265` produce real `rebar` timings without leaving the newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a((bc|de){1,})d` and `a(?P<outer>(bc|de){1,})d` workflows while leaving broader counted ranges like `{1,4}`, grouped conditionals, replacement semantics, and deeper grouped execution explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0265`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0265`.
- Reuse the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap` anchor instead of forking another manifest.
- Keep the benchmark slice narrow and sequential so broader counted ranges reopen only after this Python-path catch-up lands.

## Completion
- Promoted the existing numbered nested open-ended anchor into a measured `Pattern.fullmatch` row, added the adjacent numbered and named compile/search companions, and repointed the redundant named fullmatch row to the named nested `{1,}` slice.
- Added focused benchmark assertions and regenerated `reports/benchmarks/latest.json`; the combined benchmark report now publishes 456 workloads with 424 real `rebar` timings and 32 explicit known gaps, while the wider-ranged-repeat quantified-group manifest now carries 25 workloads with 24 measured rows and only the broader `{1,4}` grouped-alternation row left as a known gap.
