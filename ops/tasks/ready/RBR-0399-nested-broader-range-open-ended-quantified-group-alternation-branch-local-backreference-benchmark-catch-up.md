# RBR-0399: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference workflows already shown passing by the shared parity suite and published by `RBR-0397` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining outside that shared benchmark family.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by adding only the minimal numbered and named compile/module/pattern rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch success such as `abbbd` or `acccd`, one named compile companion, and one named lower-bound or longer-repetition compiled-`Pattern.fullmatch()` success such as `acccd`, `abcbccd`, `abbbbd`, or `accccd`, without widening into replacement semantics, callable replacements, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-alternation-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already shown passing by the shared parity suite and published by `RBR-0397`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0397`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- The shared nested-group alternation benchmark manifest already covers the exact, quantified `+`, and broader `{1,4}` branch-local-backreference rows, so this task should add only the directly adjacent broader-range open-ended `{2,}` measured rows needed to close that Python-path benchmark gap.
