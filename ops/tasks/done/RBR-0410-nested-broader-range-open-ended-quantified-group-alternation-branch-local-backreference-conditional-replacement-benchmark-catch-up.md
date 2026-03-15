# RBR-0410: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional replacement-template benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional replacement-template workflows supported by `RBR-0408` produce real `rebar` timings on the existing nested-group replacement manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional replacement-template slice up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path by adding only the minimal numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` replacement-template workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch row such as `abbbd` or `acccd`, one numbered mixed-branch or doubled-haystack row such as `abcbccd`, `abbbdabcbccd`, or `abcbccdaccccd`, one named row that keeps the shifted `{2,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack row that keeps the final selected `inner` branch observable, without widening into callable replacements, broader template parsing, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-replacement-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0408`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding replacement-template slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0408`, `RBR-0406`, and the existing nested-group replacement benchmark surface.
- Keep this follow-on on the existing `nested_group_replacement_boundary.py` manifest path instead of forking another benchmark family.
- The shared nested-group replacement manifest already covers the exact, quantified, open-ended `{1,}`, and broader-range `{2,}` non-conditional branch-local-backreference replacement rows, so this task should add only the directly adjacent conditional rows needed to close that Python-path benchmark gap.
- After this benchmark catch-up drains, the surviving concrete follow-on should reopen on correctness publication for the matching conditional callable-replacement slice rather than another benchmark-only pass.

## Completion
- 2026-03-15: Added four measured broader-range open-ended `{2,}` conditional replacement-template workloads to `benchmarks/workloads/nested_group_replacement_boundary.py`, keeping the existing shared manifest, cache-mode split, and module-numbered versus pattern-named coverage shape intact.
- 2026-03-15: Updated the source-tree benchmark expectations and combined-boundary assertions so `nested-group-replacement-boundary` now expects `24` measured workloads, including the new conditional numbered lower-bound / first-match-only and named lower-bound / first-match-only rows.
- 2026-03-15: Republished `reports/benchmarks/latest.py`; the tracked combined benchmark scorecard now reports `558` total workloads with `534` real `rebar` timings and `24` explicit known gaps, and `nested-group-replacement-boundary` now reports `24` measured workloads with `0` known gaps.

## Verification
- 2026-03-15: `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py -q` (`1 passed, 56 subtests passed`)
- 2026-03-15: `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q -k "nested_group_replacement_manifest_covers_broader_range_open_ended"` (`2 passed, 16 deselected, 8 subtests passed`)
- 2026-03-15: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (`{"known_gap_count": 24, "measured_workloads": 534, "module_workloads": 550, "parser_workloads": 8, "regression_workloads": 5, "total_workloads": 558}`)
