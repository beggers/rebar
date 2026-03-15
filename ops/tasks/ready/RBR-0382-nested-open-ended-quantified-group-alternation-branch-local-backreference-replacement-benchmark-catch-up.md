# RBR-0382: Catch open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template workflows supported by `RBR-0380` produce real `rebar` timings on the existing nested-group replacement manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded open-ended `{1,}` nested-group alternation plus branch-local-backreference replacement-template slice up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path by adding only the minimal numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` replacement-template workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch case such as `abbd` or `accd`, one numbered open-ended repeated-branch or mixed-haystack case such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named outer-capture case that keeps the open-ended `{1,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under template replacement, without widening into callable-replacement variants, broader template parsing, broader lower bounds like `{2,}`, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-replacement-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0380`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding replacement-template slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0380`.
- Keep this follow-on on the existing `nested_group_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent open-ended `{1,}` branch-local-backreference replacement-template rows needed to publish this exact slice cleanly; callable-replacement variants, broader template parsing, broader lower bounds like `{2,}`, and deeper nested grouped execution stay explicit gaps or out of scope.
