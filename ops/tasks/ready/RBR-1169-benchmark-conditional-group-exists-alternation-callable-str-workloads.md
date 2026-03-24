# RBR-1169: Benchmark conditional group-exists alternation callable str workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published `str` alternation-heavy conditional callable-replacement slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` workflows that the live runtime and correctness owner path already cover, before bytes mirrors, nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", callable_match_group(1, prefix="<", suffix=">"), "zzabcdezz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(callable_match_group("word", prefix="<", suffix=">"), "zzacehzz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent `str` alternation-heavy callable workloads already published on the shared correctness owner path:
  - add numbered module `sub()` and `subn()` workloads for `r"a(b)?c(?(1)(de|df)|(eg|eh))"` using `callable_match_group(1, prefix="<", suffix=">")`, with the present-arm success haystacks `zzabcdezz` and `zzabcdfzz`;
  - add numbered compiled-pattern `sub()` and `subn()` workloads for the same spelling on `zzacegzz` and `zzacehzz`, keeping the absent-capture `TypeError` outcomes explicit on the benchmark surface;
  - add named module `sub()` and `subn()` workloads for `r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` using `callable_match_group("word", prefix="<", suffix=">")`, with the matching present-arm success haystacks `zzabcdezz` and `zzabcdfzz`; and
  - add named compiled-pattern `sub()` and `subn()` workloads for the same named spelling on `zzacegzz` and `zzacehzz`, keeping the absent-capture `TypeError` outcomes explicit there too.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared callable slice expectations, representative measured workload sets, and single-manifest scorecard assertions include these eight new `str` alternation-heavy callable rows on `conditional-group-exists-boundary`;
  - preserve the already measured two-arm callable `str`/bytes rows, `count=-1` follow-ons, constant-replacement and replacement-template rows, and the surrounding nested and quantified conditional benchmark slices on the same manifest; and
  - do not widen this run into bytes alternation-heavy callable workloads, correctness publication, Rust implementation work, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the eight new measured `str` alternation-heavy callable workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1043/1043` measured workloads to `1051/1051` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 112`, `measured_workloads == 112`, and `known_gap_count == 0` to `120`, `120`, and `0`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1169-conditional-alternation-callable-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional callable benchmark file.
- Keep the scope pinned to the exact eight `str` alternation-heavy callable workloads above. Leave bytes alternation-heavy callable publication and benchmark catch-up, nested conditional callable follow-ons, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1169` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1169' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1167`:
  - `ops/tasks/done/RBR-1167-publish-conditional-group-exists-alternation-callable-str-workflows.md` completed the bounded correctness-publication slice and explicitly left same-family benchmark catch-up, bytes mirrors, and broader callable follow-ons for later;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern alternation-heavy callable `sub()` and `subn()` success and absent-capture `TypeError` workflows for this slice;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` already publish those exact eight `str` alternation-heavy callable rows on the shared conditional callable owner path; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` still stop at the simple two-arm callable rows plus the `count=-1` follow-ons in the current checkout, so the alternation-heavy callable benchmark catch-up remains the smallest surviving same-family slice and no implementation prerequisite blocks it.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` returned `1 passed, 49 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `1 passed, 4 subtests passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-alternation-callable-bench-current.py` completed successfully with `112` measured workloads and `0` known gaps, confirming the existing benchmark owner path is stable before this follow-on lands.
