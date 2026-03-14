# RBR-0295: Catch nested broader-range wider-ranged-repeat quantified-group alternation plus conditional benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the nested broader `{1,4}` grouped-alternation-plus-conditional workflows supported by `RBR-0293` produce real `rebar` timings without leaving this newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the nested broader `{1,4}` wider-ranged-repeat grouped-alternation-plus-conditional slice up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path by adding only the minimal numbered and named compile/module/pattern rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)` workflows through representative `module.compile()`, `module.search()`, and compiled-`Pattern.fullmatch()` paths, including the absent-group `else` path on `af`, lower-bound present-group hits such as `abcde` and `adede`, and mixed or upper-bound present-group paths such as `abcbcdede` and `adedededede`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0293`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0293`.
- Keep this follow-on on the existing wider-ranged-repeat grouped boundary manifest instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact bounded slice cleanly; nested grouped backtracking-heavy follow-ons, grouped replacement workflows, and broader nested grouped execution stay out of scope.

## Completion Note
- Added the seven directly adjacent numbered and named benchmark rows for `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)` to `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`, covering the absent `af` else-arm path, lower-bound `abcde` and `adede` present-group hits, the mixed `abcbcdede` present path, and the upper-bound `adedededede` all-`de` path without forking a new manifest.
- Extended the wider-ranged-repeat benchmark tests and combined benchmark expectations so the new nested broader `{1,4}` grouped-conditional rows are asserted directly instead of only changing aggregate counts.
- Republished `reports/benchmarks/latest.json`; the combined source-tree scorecard now reports 486 published workloads with 455 real `rebar` timings and 31 explicit known gaps, and the wider-ranged-repeat quantified-group manifest now reports 55 workloads with 0 known gaps.
- Verified with `python3 -m unittest tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks`, `python3 -m unittest tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_source_tree_benchmark_scorecards`, and `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`.
