# RBR-0352: Catch quantified nested-group alternation callable-replacement benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Extend the published benchmark surface so the quantified nested-group alternation callable-replacement workflows supported by `RBR-0350` produce real `rebar` timings on the existing nested-group callable-replacement manifest instead of remaining unpublished on the Python-path benchmark surface.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The benchmark harness catches the quantified nested-group alternation callable-replacement slice up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path by adding only the minimal quantified numbered and named module or compiled-`Pattern` `sub()` or `subn()` rows needed to publish this exact bounded frontier.
- `reports/benchmarks/latest.py` records real `rebar` timings for supported `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d` callable-replacement workflows through the public Python-facing `rebar` path, including one numbered lower-bound or mixed-branch case such as `abd`, `acd`, `abccd`, or `acbbd`, one numbered count-limited or first-match-only doubled-haystack case that keeps the final selected inner branch observable under replacement, one named lower-bound or repeated-branch outer-capture case that keeps the quantified outer group observable, and one named first-match-only inner-capture case on a doubled haystack.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and continue measuring through the Python-facing `rebar` module boundary so comparisons against stdlib `re` stay faithful.
- The task does not broaden regex support, fork a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0350`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current consolidated source-tree benchmark assertions instead of reviving standalone manifest-specific tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0350`.
- Keep this follow-on on the existing `nested_group_callable_replacement_boundary.py` manifest path instead of forking another benchmark family.
- Add only the directly adjacent quantified nested alternation callable-replacement rows needed to publish this exact slice cleanly; broader counted repeats like `{1,4}` or `{1,}`, branch-local-backreference callbacks, replacement-template workflows, broader callback helpers, and deeper nested grouped execution stay explicit gaps or out of scope.

## Completion Notes
- Extended `benchmarks/workloads/nested_group_callable_replacement_boundary.py` with the minimal four quantified nested-group alternation callable-replacement rows needed to publish this slice: numbered lower-bound and first-match-only `module.sub()` / `module.subn()` probes plus named repeated-branch and first-match-only `Pattern.sub()` / `Pattern.subn()` probes.
- Updated the consolidated benchmark expectations and combined boundary suite so the new quantified alternation callable rows are asserted as measured on the existing nested-group callable-replacement manifest without changing the benchmark schema or forking another family.
- Republished the tracked benchmark scorecard in `reports/benchmarks/latest.py`; the verified tracked summary is 517 total workloads, 493 measured `rebar` timings, and 24 known gaps, and the `nested-group-callable-replacement-boundary` manifest now reports 20 workloads with 20 measured rows and 0 known gaps.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --internal-probe-rebar-metadata`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report /tmp/rbr0352-nested-group-callable-replacement-bench.json`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
