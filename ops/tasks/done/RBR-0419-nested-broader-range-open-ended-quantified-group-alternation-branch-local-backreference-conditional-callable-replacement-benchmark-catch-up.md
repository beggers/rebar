# RBR-0419: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement workflows supported by `RBR-0415` produce real `rebar` timings on the existing nested-group callable benchmark manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by adding only the minimal four measured rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch case such as `abbbd` or `acccd`, one numbered first-match-only or mixed-branch case such as `abbbdabcbccd`, `abcbccdaccccd`, or a leading `acccd` match, one named row that keeps the shifted `{2,}` `outer` capture observable under replacement, and one named first-match-only row that keeps the final selected `inner` branch observable, without widening into non-conditional rows, replacement-template variants, broader callback semantics, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-callable-replacement-boundary` as the shared benchmark surface for this slice, raise that manifest's measured workload count from `40` to `44`, and keep its `known_gap_count` at `0`.
- The updated combined benchmark report adds four real `rebar` timings for this slice while keeping the overall explicit known-gap count unchanged and preserving Python-path adapter provenance.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0415`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding callable-replacement slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0415`, `RBR-0414`, `RBR-0410`, and the existing nested-group callable benchmark surface.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- The shared callable benchmark manifest already covers the exact, quantified `+`, broader `{1,4}`, open-ended `{1,}`, and broader-range `{2,}` non-conditional branch-local-backreference callable rows, so this task should add only the directly adjacent broader-range open-ended `{2,}` conditional rows needed to close that Python-path benchmark gap.
- The adjacent published callable-replacement correctness fixture family currently stops at this bounded conditional slice, so once this benchmark catch-up drains no concrete post-drain feature follow-on is pinned yet.

## Completion Notes
- 2026-03-15: Added the minimal four broader-range open-ended `{2,}` conditional callable benchmark rows on the existing `nested_group_callable_replacement_boundary.py` path: numbered warm `module.sub()` and `module.subn()` lower-bound / first-match-only probes plus named purged `Pattern.sub()` and `Pattern.subn()` lower-bound / first-match-only probes for `a((b|c){2,})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`.
- 2026-03-15: Updated the shared source-tree benchmark expectations so `nested-group-callable-replacement-boundary` now publishes `44` measured workloads with `0` known gaps, and refreshed `reports/benchmarks/latest.py` to `562` total workloads, `538` real `rebar` timings, and the same `24` explicit known gaps.
- 2026-03-15: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k "nested_broader_range_open_ended_conditional"`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
