# RBR-1175: Benchmark conditional group-exists alternation callable bytes workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published bytes alternation-heavy conditional callable-replacement slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` workflows that the live runtime and correctness owner path already cover, before nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(de|df)|(eg|eh))", callable_match_group(1, prefix=b"<", suffix=b">"), b"zzabcdezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(callable_match_group("word", prefix=b"<", suffix=b">"), b"zzacehzz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent bytes alternation-heavy callable workloads already published on the shared correctness owner path:
  - add numbered module `sub()` and `subn()` workloads for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` using `callable_match_group(1, prefix=b"<", suffix=b">")`, with the present-arm success haystacks `b"zzabcdezz"` and `b"zzabcdfzz"`;
  - add numbered compiled-pattern `sub()` and `subn()` workloads for the same spelling on `b"zzacegzz"` and `b"zzacehzz"`, keeping the absent-capture `TypeError` outcomes explicit on the benchmark surface;
  - add named module `sub()` and `subn()` workloads for `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` using `callable_match_group("word", prefix=b"<", suffix=b">")`, with the matching present-arm success haystacks `b"zzabcdezz"` and `b"zzabcdfzz"`; and
  - add named compiled-pattern `sub()` and `subn()` workloads for the same named spelling on `b"zzacegzz"` and `b"zzacehzz"`, keeping the absent-capture `TypeError` outcomes explicit there too.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared callable slice expectations, representative measured workload sets, and single-manifest scorecard assertions include these eight new bytes alternation-heavy callable rows on `conditional-group-exists-boundary`;
  - preserve the already measured two-arm callable `str`/bytes rows, `count=-1` follow-ons, replacement-template rows, constant-replacement rows, and the adjacent alternation-heavy `str` callable rows plus surrounding nested and quantified conditional benchmark slices on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, nested conditional callable benchmarks, quantified conditional callable benchmarks, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the eight new measured bytes alternation-heavy callable workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1051/1051` measured workloads to `1059/1059` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - `REPORT["manifests"]["conditional-group-exists-boundary"]` moves from `workload_count == 120`, `measured_workloads == 120`, and `known_gap_count == 0` to `128`, `128`, and `0`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1175-conditional-alternation-callable-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional callable benchmark file.
- Keep the scope pinned to the exact eight bytes alternation-heavy callable workloads above. Leave nested conditional callable follow-ons, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1175` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1175|alternation-callable-bytes-workloads|conditional group-exists alternation callable bytes workloads' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files and an architecture-task note, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1173`:
  - `ops/tasks/done/RBR-1173-publish-conditional-group-exists-alternation-callable-bytes-workflows.md` completed the bounded bytes correctness-publication slice and explicitly left same-family benchmark catch-up, nested callable follow-ons, and quantified callable follow-ons for later;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the exact eight bytes alternation-heavy callable rows on the shared conditional callable owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` still stop at the adjacent alternation-heavy `str` callable rows in the current checkout, so the bytes benchmark mirror is the smallest surviving same-family slice and no implementation prerequisite blocks it; and
  - the current tracked benchmark report is fully measured at `1051/1051` workloads across `30` manifests, so this follow-on is a pure publication expansion rather than a gap-closing repair.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` returned `1 passed, 50 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` returned `1 passed, 4 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-rbr-1175-current.py` completed successfully with `120` measured workloads and `0` known gaps; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-rbr-1175-full-current.py` completed successfully with `1051` measured workloads and `0` known gaps.

## Completion
- Added the exact eight bytes alternation-heavy conditional callable `sub()`/`subn()` benchmark rows to `benchmarks/workloads/conditional_group_exists_boundary.py` on the existing shared owner path, keeping the absent-capture `TypeError` pattern-entrypoint rows explicit.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared alternation-heavy callable slice expectations and scorecard representative assertions now cover both the existing `str` rows and the new bytes rows.
- Republished `reports/benchmarks/latest.py`; the tracked combined benchmark report now shows `1059` measured workloads with `0` known gaps across `30` manifests, and `REPORT["manifests"]["conditional-group-exists-boundary"]` now shows `128` workloads, `128` measured workloads, and `0` known gaps.
- Verification completed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_source_tree_combined_slice_filters_match_expected_manifest_rows` -> `1 passed, 50 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_single_manifest_scorecards_keep_slice_backed_representatives` -> `1 passed, 4 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1175-conditional-alternation-callable-bytes.py` -> `128` measured workloads / `0` known gaps
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` -> `1059` measured workloads / `0` known gaps
