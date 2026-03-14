# RBR-0340: Catch nested broader-range wider-ranged-repeat quantified-group alternation plus branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference workflows supported by `RBR-0338` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining unpublished on the benchmark side.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by adding only the minimal adjacent numbered and named compile/module/pattern rows needed to publish this exact frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch `module.search()` success such as `abbd` or `accd`, one named broader counted-repeat or upper-bound `Pattern.fullmatch()` success such as `abccd`, `abcbccd`, or `acccccd`, and one bounded compile companion that keeps the broader `{1,4}` slice observable without widening into open-ended counted repeats, replacement semantics, conditionals, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0338`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0338`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact slice cleanly; open-ended counted repeats, replacement workflows, conditionals, and deeper nested grouped execution stay out of scope.
