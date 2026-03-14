# RBR-0334: Catch quantified nested-group-alternation-plus-branch-local-backreference benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the bounded quantified nested-group-alternation-plus-branch-local-backreference workflows supported by `RBR-0332` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining unpublished on the benchmark side.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded quantified nested-group-alternation-plus-branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by adding only the minimal adjacent numbered and named compile/module/pattern rows needed to publish this exact frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d` workflows through the public Python-facing `rebar` path, including a lower-bound same-branch success such as `abbd` or `accd`, a repeated-branch success such as `abbbd` or `abccd`, and one bounded numbered or named compile/module companion that keeps the quantified outer capture plus final inner branch observable without widening into broader counted repeats, replacement semantics, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0332`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0332`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent numbered and named rows needed to publish this exact slice cleanly; broader counted repeats, replacement workflows, conditionals, and deeper nested grouped execution stay explicit gaps or out of scope.
