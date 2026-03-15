# RBR-0370: Catch broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement workflows supported by `RBR-0368` produce real `rebar` timings on the existing nested-group callable-replacement manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by adding only the minimal numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch case such as `abbd` or `accd`, one numbered broader repeated-branch or first-match-only case such as `abbbdaccd`, `abcbccdabbd`, or `zzaccdabcbccdzz`, one named outer-capture case such as `abcbccd` or `zzacccccdzz`, and one named first-match-only or doubled-haystack case such as `abbbdaccd` or `zzacccccdabbbdzz`, without widening into open-ended counted repeats like `{1,}`, replacement-template variants, broader callback semantics, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-callable-replacement-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0368`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding callable-replacement slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0368`.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent broader `{1,4}` branch-local-backreference callable rows needed to publish this exact slice cleanly; open-ended counted repeats like `{1,}`, replacement-template workflows, broader callback helpers, and deeper nested grouped execution stay explicit gaps or out of scope.

## Completion Notes
- Extended `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with the minimal four broader `{1,4}` branch-local-backreference callable rows needed to publish this slice: numbered `module.sub()` and `module.subn()` probes on `abbd` and `abcbccdabbd`, plus named `Pattern.sub()` and `Pattern.subn()` probes on `zzacccccdzz` and `zzacccccdabbbdzz`.
- Updated the shared benchmark assertions so the existing `nested-group-callable-replacement-boundary` manifest now has a manifest-local scorecard case for these broader rows and a focused combined-suite check that locks this exact bounded `{1,4}` callback slice to the existing shared manifest path while keeping the earlier quantified-only check scoped away from counted-repeat rows.
- Republished the tracked benchmark scorecard in `reports/benchmarks/latest.py`; the verified tracked summary is `529` total workloads, `505` measured `rebar` timings, and `24` known gaps, and the tracked `nested-group-callable-replacement-boundary` manifest now reports `32` workloads with `32` measured rows and `0` known gaps.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k nested_group_callable_replacement_manifest`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report /tmp/rbr0370-nested-group-callable-replacement-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
