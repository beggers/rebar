# RBR-0399: Catch broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference workflows already shown passing by the shared parity suite and published by `RBR-0397` produce real `rebar` timings on the existing nested-group alternation manifest instead of remaining outside that shared benchmark family.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference slice up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path by adding only the minimal numbered and named compile/module/pattern rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d` workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch success such as `abbbd` or `acccd`, one named compile companion, and one named lower-bound or longer-repetition compiled-`Pattern.fullmatch()` success such as `acccd`, `abcbccd`, `abbbbd`, or `accccd`, without widening into replacement semantics, callable replacements, broader lower bounds, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-alternation-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already shown passing by the shared parity suite and published by `RBR-0397`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0397`.
- Keep this follow-on on the existing `nested_group_alternation_boundary.py` manifest path instead of forking another benchmark family.
- The shared nested-group alternation benchmark manifest already covers the exact, quantified `+`, and broader `{1,4}` branch-local-backreference rows, so this task should add only the directly adjacent broader-range open-ended `{2,}` measured rows needed to close that Python-path benchmark gap.

## Completion
- Added the minimal broader-range open-ended `{2,}` branch-local trio on `benchmarks/workloads/nested_group_alternation_boundary.py`: one numbered `module.search()` lower-bound success on `zzabbbdzz`, one named `module.compile()` companion, and one named `Pattern.fullmatch()` lower-bound success on `acccd`.
- Updated the shared combined benchmark expectations so `nested-group-alternation-boundary` now treats the new `{2,}` rows as a fourth measured branch-local slice distinct from the existing non-quantified, `+`, and `{1,4}` rows.
- Republished `reports/benchmarks/latest.py`; the tracked combined scorecard now reports `548` total workloads, `524` measured `rebar` timings, and `24` explicit known gaps, while the tracked `nested-group-alternation-boundary` manifest reports `22` workloads with `22` measured rows and `0` gaps.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report /tmp/rbr0399-nested-group-alternation.json`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k nested_group_alternation_manifest`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
