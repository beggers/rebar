# RBR-1159: Benchmark conditional group-exists callable str negative-count workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published `str count=-1` conditional callable-replacement slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` workflows that the live runtime and correctness owner path already cover, before broader callable follow-ons widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", callable_match_group(1, suffix="x"), "abcdaceabcd", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(callable_match_group("word", suffix="x"), "abcdaceabcd", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent `str count=-1` callable workloads already published on the shared correctness owner path:
  - add the numbered module `sub()` `str` workload for `r"a(b)?c(?(1)d|e)"` with a `callable_match_group` replacement targeting group `1`, haystack `"abcdaceabcd"`, suffix `"x"`, and `count == -1`;
  - add the named module `subn()` `str` workload for `r"a(?P<word>b)?c(?(word)d|e)"` with a `callable_match_group` replacement targeting group `"word"`, haystack `"abcdaceabcd"`, suffix `"x"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` `str` workload for `r"a(b)?c(?(1)d|e)"` with the same callable descriptor, haystack, and `count == -1`; and
  - add the named compiled-pattern `subn()` `str` workload for `r"a(?P<word>b)?c(?(word)d|e)"` with the same callable descriptor, haystack, and `count == -1`.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared callable slice expectations and single-manifest scorecard representatives include these four new negative-count `str` workloads on `conditional-group-exists-boundary`;
  - preserve the already measured present, first-match-only, absent-exception, and bytes callable rows plus the surrounding template, alternation-heavy, nested, and quantified conditional benchmark slices on the same manifest; and
  - do not widen this benchmark surface into new correctness publication, bytes negative-count callable work, new callable helper shapes beyond `callable_match_group`, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the four new measured `str` negative-count workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1035/1035` measured workloads to `1039/1039` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 104`, `measured_workloads == 104`, and `known_gap_count == 0` to `108`, `108`, and `0`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1159-conditional-callable-negative-count-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional callable benchmark file.
- Keep the scope pinned to the exact four `str count=-1` workloads above. Leave broader callable follow-ons, additional callback shapes, alternation-heavy conditionals, nested conditionals, quantified conditionals, and other replacement-owner families for later tasks.

## Notes
- `RBR-1159` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1159' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1157`:
  - `ops/tasks/done/RBR-1157-publish-conditional-group-exists-callable-str-negative-count-workflows.md` closed the adjacent correctness publication and explicitly left same-family benchmark catch-up for later on this bounded conditional callable family;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the exact four `str count=-1` callable rows on the shared conditional callable owner path;
  - `rg -n 'negative-count.*callable|callable.*negative-count' benchmarks/workloads/conditional_group_exists_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, confirming the published benchmark surface still omits this exact negative-count callable slice; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-callable-bench-current.py` completed successfully with `104` measured workloads and `0` known gaps in this run, confirming the benchmark owner path is live and the runtime prerequisite is already landed.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` returned `1 passed, 49 subtests passed` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `1 passed, 4 subtests passed` in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-callable-bench-current.py` completed successfully with `104` measured workloads and `0` known gaps in this run.
