# RBR-0346: Catch nested-group alternation callable-replacement benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the bounded nested-group alternation callable-replacement workflows supported by `RBR-0344` produce real `rebar` timings on the existing nested-group callable-replacement manifest instead of remaining only as an explicit known-gap row.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded nested-group alternation callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by promoting the current `module-sub-callable-nested-group-alternation-cold-gap` row and adding only the minimal adjacent numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered `b`-branch or mixed-branch case such as `abd`, `abdacd`, or `acdabd`, one numbered first-match-only compiled-`Pattern` case that keeps the selected inner branch observable, one named outer-capture case such as `acd` or `abdacd`, and one named count-limited inner-capture case that keeps the final selected branch observable without widening into quantified nested alternation callbacks, branch-local-backreference callbacks, replacement-template variants, broader callback semantics, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0344`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0344`.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent numbered and named callable-replacement rows needed to publish this exact slice cleanly; quantified nested alternation callbacks, branch-local-backreference callbacks, replacement-template workflows, broader callback helpers, and deeper nested grouped execution stay explicit gaps or out of scope.
