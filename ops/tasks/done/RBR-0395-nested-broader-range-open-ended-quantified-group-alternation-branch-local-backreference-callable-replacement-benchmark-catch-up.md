# RBR-0395: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference callable-replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference callable-replacement workflows already shown passing by `RBR-0390` produce real `rebar` timings on the existing nested-group callable-replacement manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by adding only the minimal numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch case such as `abbbd` or `acccd`, one numbered mixed-branch or longer-repetition case such as `abcbccd`, `abbbbd`, `accccd`, `abbbdabcbccd`, or `abcbccdabbbd`, one named outer-capture case that keeps the broader-range open-ended `{2,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under replacement, without widening into replacement-template variants, broader callback semantics, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-callable-replacement-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already shown passing by `RBR-0390`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding callable-replacement slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0390`; stale follow-on `RBR-0392` was retired because the broader-range open-ended `{2,}` callable-replacement parity already passes through the shared public API.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- The shared callable benchmark manifest already covers the exact, quantified, broader `{1,4}`, and open-ended `{1,}` branch-local-backreference callable rows, so this task should add only the directly adjacent broader-range open-ended `{2,}` measured rows needed to close that Python-path benchmark gap.

## Completion
- Extended `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with four measured broader-range open-ended `{2,}` callable-replacement rows for `a((b|c){2,})\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`, keeping the slice on the shared nested-group callable benchmark manifest and preserving the prior `{1,}` rows.
- Updated the source-tree benchmark expectation tables and combined-suite callable assertions so the older `{1,}` open-ended slice remains explicit while the new `{2,}` broader-range slice gets its own measured-row coverage through the existing shared manifest path.
- Republished `reports/benchmarks/latest.py`; the tracked combined benchmark scorecard is now `545` total workloads, `521` measured workloads, and `24` known gaps, and `nested-group-callable-replacement-boundary` now records `40` measured workloads with `0` gaps.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_runner_regenerates_source_tree_scorecards tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_nested_group_callable_replacement_manifest_covers_open_ended_branch_local_backreference_slice tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_nested_group_callable_replacement_manifest_covers_broader_range_open_ended_branch_local_backreference_slice -q`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
