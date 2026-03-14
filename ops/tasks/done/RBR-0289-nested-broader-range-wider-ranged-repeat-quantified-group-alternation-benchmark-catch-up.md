# RBR-0289: Catch nested broader-range wider-ranged-repeat quantified-group alternation benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the nested broader `{1,4}` grouped-alternation workflows supported by `RBR-0287` produce real `rebar` timings without leaving this newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the nested broader `{1,4}` wider-ranged-repeat grouped-alternation slice up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path by adding only the minimal numbered and named compile/module/pattern rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d` workflows through representative `module.compile()`, `module.search()`, and compiled-`Pattern.fullmatch()` paths, including lower-bound successes such as `abcd` and `aded`, mixed mid-range paths such as `abcbcded`, and upper-bound paths such as `adedededed`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0287`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0287`.
- Keep the nested broader `{1,4}` grouped-alternation follow-on on the existing wider-ranged-repeat grouped boundary manifest instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact bounded slice cleanly; nested grouped conditionals, nested grouped backtracking-heavy follow-ons, replacement workflows, and broader nested grouped execution stay out of scope.

## Completion Note
- Added the six minimal numbered and named `module.compile()`, `module.search()`, and `Pattern.fullmatch()` workloads for `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d` to `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`, using the bounded `abcd`/`aded`, `abcbcded`, and `adedededed` benchmark inputs required by the task.
- Republished `reports/benchmarks/latest.json`; the combined source-tree scorecard now reports 479 published workloads with 448 real `rebar` timings and 31 explicit known gaps, and the wider-ranged-repeat quantified-group manifest now reports 48 workloads with 0 known gaps.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json --report .rebar/tmp-rbr-0289-single.json`, `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, and `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_source_tree_benchmark_scorecards`.
