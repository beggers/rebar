# RBR-1163: Benchmark conditional group-exists callable bytes negative-count workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published bytes `count=-1` conditional callable-replacement slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` workflows that the live runtime and correctness owner path already cover, before any broader callable follow-on widens this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", callable_match_group(1, suffix=b"x"), b"abcdaceabcd", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(callable_match_group("word", suffix=b"x"), b"abcdaceabcd", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent bytes `count=-1` callable workloads already published on the shared correctness owner path:
  - add the numbered module `sub()` bytes workload for `rb"a(b)?c(?(1)d|e)"` with a `callable_match_group` replacement targeting group `1`, haystack `b"abcdaceabcd"`, suffix `b"x"`, and `count == -1`;
  - add the named module `subn()` bytes workload for `rb"a(?P<word>b)?c(?(word)d|e)"` with a `callable_match_group` replacement targeting group `"word"`, haystack `b"abcdaceabcd"`, suffix `b"x"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` bytes workload for `rb"a(b)?c(?(1)d|e)"` with the same callable descriptor, haystack, and `count == -1`; and
  - add the named compiled-pattern `subn()` bytes workload for `rb"a(?P<word>b)?c(?(word)d|e)"` with the same callable descriptor, haystack, and `count == -1`.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared callable slice expectations and single-manifest scorecard representatives include these four new bytes negative-count workloads on `conditional-group-exists-boundary`;
  - preserve the already measured bytes present, first-match-only, and absent-exception callable rows plus the already measured `str` negative-count callable rows and surrounding template, alternation-heavy, nested, and quantified conditional benchmark slices on the same manifest; and
  - do not widen this benchmark surface into new correctness publication, new callable helper shapes beyond `callable_match_group`, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the four new measured bytes negative-count workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1039/1039` measured workloads to `1043/1043` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 108`, `measured_workloads == 108`, and `known_gap_count == 0` to `112`, `112`, and `0`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1163-conditional-callable-negative-count-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional callable benchmark file.
- Keep the scope pinned to the exact four bytes `count=-1` workloads above. Leave broader callable follow-ons, additional callback shapes, alternation-heavy conditionals, nested conditionals, quantified conditionals, and other replacement-owner families for later tasks.

## Notes
- `RBR-1163` is unreserved in the live queue for this run:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this checkout; and
  - `rg -n 'RBR-1163' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1161`:
  - `ops/tasks/done/RBR-1161-publish-conditional-group-exists-callable-bytes-negative-count-workflows.md` closed the adjacent correctness publication and explicitly left same-family benchmark catch-up for later on this bounded conditional callable family;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` already publish the exact four bytes `count=-1` callable rows on the shared conditional callable owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` still omit the four matching bytes negative-count benchmark ids in this run, even though the same owner path already carries the surrounding bytes callable present, first-match-only, and absent-exception rows plus the adjacent `str` negative-count catch-up; and
  - the existing benchmark owner path is already live with `108` measured workloads and `0` known gaps in the current checkout, so no implementation prerequisite blocks this benchmark publication.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` returned `1 passed, 49 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `1 passed, 4 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-callable-bench-current.py` completed successfully with `108` measured workloads and `0` known gaps`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_module_bytes_callable_replacement_negative_count_short_circuits_without_callback tests/python/test_callable_replacement_parity_suite.py::test_pattern_bytes_callable_replacement_negative_count_short_circuits_without_callback` returned `200 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `24` executed and `24` passed, while `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-full-correctness.py` returned `1677` executed and `1677` passed`.

## Completion
- Added the exact four bytes `count=-1` callable replacement workloads on the existing `conditional-group-exists-boundary` manifest path for numbered module `sub()`, named module `subn()`, numbered compiled-pattern `sub()`, and named compiled-pattern `subn()`.
- Updated the shared source-tree combined benchmark expectations so the conditional callable slice and single-manifest representative workload sets include the new bytes negative-count rows without widening the manifest family.
- Regenerated the tracked combined benchmark publication. Verified from `reports/benchmarks/latest.py` that the combined summary now reports `1043` measured workloads out of `1043` total with `known_gap_count == 0`, and `REPORT["manifests"]["conditional-group-exists-boundary"]` now reports `workload_count == 112`, `measured_workloads == 112`, and `known_gap_count == 0`.
- Verification run results in this implementation pass:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` returned `1 passed, 49 subtests passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `1 passed, 4 subtests passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1163-conditional-callable-negative-count-bytes.py` returned `112` measured workloads and `0` known gaps.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1043` measured workloads and `0` known gaps.
