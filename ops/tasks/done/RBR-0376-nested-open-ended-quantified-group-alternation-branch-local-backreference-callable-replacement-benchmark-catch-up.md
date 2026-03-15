# RBR-0376: Catch open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the bounded open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement workflows supported by `RBR-0374` produce real `rebar` timings on the existing nested-group callable-replacement manifest instead of remaining correctness-only coverage.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the bounded open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by adding only the minimal numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered lower-bound same-branch case such as `abbd` or `accd`, one numbered open-ended repeated-branch or mixed-haystack case such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named outer-capture case that keeps the open-ended `{1,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under replacement, without widening into replacement-template variants, broader callback semantics, broader lower bounds like `{2,}`, or deeper nested grouped execution.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The updated benchmark assertions in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keep `nested-group-callable-replacement-boundary` as the shared benchmark surface for this slice instead of reviving a manifest-specific wrapper.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0374`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding callable-replacement slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0374`.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent open-ended `{1,}` branch-local-backreference callable rows needed to publish this exact slice cleanly; replacement-template workflows, broader callback helpers, broader lower bounds like `{2,}`, and deeper nested grouped execution stay explicit gaps or out of scope.

## Completion
- Added four measured open-ended `{1,}` callable benchmark rows to `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, keeping this slice on the shared nested-group callable manifest while covering the numbered lower-bound and first-match-only workflows plus the named outer-capture and first-match-only workflows for `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d`.
- Updated the shared benchmark expectations and combined benchmark assertions so `nested-group-callable-replacement-boundary` now expects 36 measured workloads and explicitly validates the new open-ended branch-local-backreference rows without reviving a manifest-specific wrapper.
- Republished `reports/benchmarks/latest.py`; the tracked combined report now shows 533 total workloads, 509 measured `rebar` timings, and 24 explicit known gaps, and the `nested-group-callable-replacement-boundary` manifest now reports 36 measured workloads with 0 gaps.
- Verified with `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py -q`, `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
