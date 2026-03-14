# RBR-0278: Catch broader-range wider-ranged-repeat quantified-group alternation backtracking-heavy benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the broader `{1,4}` grouped backtracking-heavy workflows supported by `RBR-0276` produce real `rebar` timings without leaving this newly supported slice absent from benchmark reporting.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the broader `{1,4}` wider-ranged-repeat grouped backtracking-heavy slice up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path by adding only the minimal numbered and named compile/module/pattern rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported `a((bc|b)c){1,4}d` and `a(?P<word>(bc|b)c){1,4}d` workflows through representative compile, `module.search()`, and compiled-`Pattern.fullmatch()` paths, including lower-bound short- and long-branch hits like `abcd` and `abccd`, mixed second-repetition paths like `abcbccd` or `abccbcd`, and one bounded four-repetition mixed path like `abcbccbccbcd`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` path so comparisons against stdlib `re` stay faithful at the module boundary.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0276`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0276`.
- Keep the broader `{1,4}` grouped backtracking-heavy follow-on on the existing wider-ranged-repeat grouped boundary manifest instead of forking another benchmark family.
- Add only the directly adjacent broader-range grouped backtracking-heavy rows needed to publish this exact slice cleanly; open-ended grouped backtracking, grouped conditionals, replacement workflows, and broader grouped execution stay out of scope.
