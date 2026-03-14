# RBR-0316: Catch quantified nested-group callable-replacement benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the quantified nested-group callable-replacement workflows supported by `RBR-0313` produce real `rebar` timings without leaving this newly supported slice represented only as an explicit gap row.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the quantified nested-group callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by promoting the current quantified named `Pattern.subn()` gap row and adding only the minimal adjacent numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for supported `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` callable-replacement workflows through the public Python-facing `rebar` path, including a lower-bound one-repetition case such as `abcd`, a repeated-inner-capture case such as `abcbcd`, and one bounded count-limited or first-match-only case on `abcbcdabcbcd`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0313`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0313`.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent quantified numbered and named callable-replacement rows needed to publish this exact slice cleanly; alternation inside the repeated site, broader counted repeats, and deeper nested grouped execution stay explicit gaps or out of scope.
