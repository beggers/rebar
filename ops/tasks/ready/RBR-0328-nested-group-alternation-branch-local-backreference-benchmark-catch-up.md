# RBR-0328: Catch nested-group-alternation-plus-branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the bounded nested-group-alternation-plus-branch-local-backreference workflows supported by `RBR-0326` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining only as an explicit known-gap row.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded nested-group-alternation-plus-branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by promoting the current named compiled-`Pattern.fullmatch()` gap row and adding only the minimal adjacent numbered and named compile/module/pattern rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` workflows through the public Python-facing `rebar` path, including one numbered branch-local-backreference success such as `abbd`, one named success such as `accd`, and one bounded module or compile companion that keeps the slice observable without widening into quantified nested backreferences, broader counted repeats, replacement semantics, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0326`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0326`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact slice cleanly; quantified nested backreferences, broader counted repeats, replacement workflows, and deeper nested grouped execution stay explicit gaps or out of scope.
