# RBR-0404: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional workflows supported by `RBR-0402` produce real `rebar` timings on the existing `branch_local_backreference_boundary.py` manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/branch_local_backreference_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional slice up on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` path by adding only the minimal numbered and named compile/module/pattern rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` workflows through the public Python-facing `rebar` path, including one numbered compile companion, one numbered `module.search()` lower-bound or mixed-branch success such as `zzabbbdzz`, `zzacccdzz`, or `zzabcbccdzz`, one numbered `Pattern.fullmatch()` success such as `abbbd`, `acccd`, or `abcbccd`, and named companions that keep `outer` and the final `inner` branch observable, without widening into replacement semantics, callable replacements, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `branch-local-backreference-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0402`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0402`.
- Keep this follow-on on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` manifest path instead of forking another benchmark family.
- The shared branch-local benchmark manifest already covers the bounded base conditional rows and the adjacent nested branch-local rows, so this task should add only the directly adjacent broader-range open-ended `{2,}` conditional rows needed to close that Python-path benchmark gap.
- After this benchmark catch-up drains, the surviving frontier should reopen on correctness publication for the matching conditional replacement-template slice rather than another benchmark-only pass.

## Completion
- Added six measured rows to `benchmarks/workloads/branch_local_backreference_boundary.py` for the bounded numbered and named compile, `module.search()`, and `Pattern.fullmatch()` workflows on `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`, using the existing shared branch-local manifest and source-tree shim timing path instead of forking another benchmark family.
- Extended the shared benchmark assertions in `tests/benchmarks/benchmark_expectations.py` with a dedicated `branch-local-backreference-boundary` source-tree scorecard case and representative measured IDs for the six new workloads, and added a combined-suite assertion in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` that locks their exact IDs, patterns, and haystacks onto the existing shared benchmark surface.
- Verified the shared benchmark scorecard path with `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py` (`1 passed`).
- Verified the shared combined benchmark surface with `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`17 passed`).
- Republished the tracked combined benchmark report in `reports/benchmarks/latest.py`; the tracked summary is `554` total workloads, `530` measured `rebar` timings, and `24` known gaps, while the tracked `branch-local-backreference-boundary` manifest summary now shows `24` measured workloads and `0` known gaps.
- The remaining bounded follow-on for this frontier is correctness-publication task `RBR-0406` for the matching replacement-template `sub()` / `subn()` slice.
