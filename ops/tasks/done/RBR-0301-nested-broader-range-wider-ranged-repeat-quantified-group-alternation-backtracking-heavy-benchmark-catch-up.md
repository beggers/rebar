# RBR-0301: Catch nested broader-range wider-ranged-repeat quantified-group alternation backtracking-heavy benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the nested broader `{1,4}` grouped backtracking-heavy workflows supported by `RBR-0299` produce real `rebar` timings without leaving this newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the nested broader `{1,4}` wider-ranged-repeat grouped backtracking-heavy slice up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path by adding only the minimal numbered and named compile/module/pattern rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d` workflows through representative `module.compile()`, `module.search()`, and compiled-`Pattern.fullmatch()` paths, including lower-bound short- and long-branch hits such as `abcd` and `abccd`, mixed second-repetition paths such as `abcbccd` and `abccbcd`, and one bounded four-repetition mixed path such as `abcbccbccbcd`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0299`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0299`.
- Keep this follow-on on the existing wider-ranged-repeat grouped boundary manifest instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact bounded slice cleanly; grouped replacement workflows and broader nested grouped execution stay out of scope.

## Completion
- Added seven nested broader `{1,4}` grouped backtracking-heavy benchmark rows on the existing `wider_ranged_repeat_quantified_group_boundary` manifest for `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d`, covering the lower-bound short and long hits plus mixed second-repetition and four-repetition success paths called out by the task.
- Extended the targeted benchmark suite to assert the new rows are present, categorized as nested backtracking-heavy grouped workloads, and measured through the Python-path benchmark surface.
- Republished `reports/benchmarks/latest.json`; the combined report now records 493 workloads, 462 measured `rebar` timings, and 31 known gaps, while the widened-repeat grouped manifest now reports 62 workloads, 62 measured, and 0 known gaps.
- Verified with `python3 -m json.tool benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks`, a narrow temp-manifest benchmark run, and a full `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json` republish.
