# RBR-0307: Catch quantified nested-group replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Extend the published benchmark surface so the quantified nested-group replacement-template workflows supported by `RBR-0305` produce real `rebar` timings without leaving this newly supported slice represented only as an explicit gap row.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness catches the quantified nested-group replacement slice up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path by promoting the current quantified gap row and adding only the minimal adjacent numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed for this exact bounded frontier.
- `reports/benchmarks/latest.json` records real `rebar` timings for supported `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` replacement-template workflows through the public Python-facing `rebar` path, including a lower-bound one-repetition case such as `abcd`, a repeated-inner-capture case such as `abcbcd`, and one bounded count-limited or first-match-only case on `abcbcdabcbcd`.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0305`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0305`.
- Keep this follow-on on the existing `nested_group_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent quantified numbered and named replacement-template rows needed to publish this exact slice cleanly; callable replacement, alternation inside the repeated site, broader counted repeats, and deeper nested grouped execution stay out of scope.

## Completion Notes
- Promoted the existing quantified named `Pattern.subn()` anchor on `benchmarks/workloads/nested_group_replacement_boundary.py` into a measured first-match-only row on `zzabcbcdabcbcdzz` and added three adjacent quantified measured rows for the numbered lower-bound module `sub()`, numbered first-match-only module `subn()`, and named repeated-inner-capture `Pattern.sub()` workflows.
- Updated the combined source-tree benchmark expectations so the quantified numbered and named workload IDs are asserted as measured in the consolidated boundary suite instead of leaving only the former gap-anchor ID represented.
- Republished `reports/benchmarks/latest.json`; the combined source-tree benchmark report now covers 496 workloads with 466 real `rebar` timings and 30 explicit known gaps, while the nested-group replacement manifest now reports 12 measured workloads and 0 known gaps.
- Verified with `cargo build -p rebar-cpython`, a narrow `PYTHONPATH=python python3 -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_replacement_boundary.py` run, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and a full `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json` republish.
