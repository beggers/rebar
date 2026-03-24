# RBR-1155: Benchmark conditional group-exists template str negative-count workloads

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published `str count=-1` conditional replacement-template slice up on the existing Python-path benchmark surface by measuring the exact four bounded module and compiled-`Pattern` workflows that already match CPython on the shared owner path, before callable follow-ons or broader conditional replacement work widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", r"\1x", "abcdaceabcd", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(r"\g<word>x", "abcdaceabcd", -1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the four adjacent `str count=-1` replacement-template workloads already published on the shared correctness owner path:
  - add the numbered module `sub()` `str` workload for `r"a(b)?c(?(1)d|e)"` with `r"\1x"`, `"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` `str` workload for `r"a(?P<word>b)?c(?(word)d|e)"` with `r"\g<word>x"`, `"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` `str` workload for `r"a(b)?c(?(1)d|e)"` with `r"\1x"`, `"abcdaceabcd"`, and `count == -1`; and
  - add the named compiled-pattern `subn()` `str` workload for `r"a(?P<word>b)?c(?(word)d|e)"` with `r"\g<word>x"`, `"abcdaceabcd"`, and `count == -1`.
- Keep the work on the existing `conditional-group-exists-boundary` benchmark owner path instead of creating another manifest or detached benchmark test module:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared conditional replacement-template slice expectations, representative measured rows, and template payload round-trip assertions include these four new negative-count `str` workloads on `conditional-group-exists-boundary`;
  - preserve the already measured present/absent `str` and bytes template rows, the already-landed bytes negative-count rows, and the surrounding callable, alternation-heavy, nested, and quantified conditional benchmark slices on the same manifest; and
  - do not widen this benchmark surface into new callable rows, new correctness publication, or another conditional benchmark family.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the tracked report gains the four new measured `str` negative-count workloads for `conditional-group-exists-boundary`;
  - the combined benchmark summary moves from `1031/1031` measured workloads to `1035/1035` measured workloads with `known_gap_count == 0`;
  - the manifest count stays at `30`; and
  - do not widen this run into Rust implementation work, correctness fixtures or reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1155-conditional-template-negative-count-str.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not change Rust implementation files, `python/rebar/__init__.py`, correctness fixtures, correctness reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark test module, or a detached conditional replacement benchmark file.
- Keep the scope pinned to the exact four `str count=-1` workloads above. Leave same-family callable follow-ons, broader replacement-owner families, and any deeper conditional benchmark expansion for later tasks.

## Notes
- `RBR-1155` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1155|RBR-1156|RBR-1157' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files or no matches at all, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1153`:
  - `ops/tasks/done/RBR-1151-implement-conditional-group-exists-template-str-negative-count-parity.md` closed by proving the bounded `str count=-1` module and compiled-pattern runtime behaviors already match CPython on this branch;
  - `ops/tasks/done/RBR-1153-publish-conditional-group-exists-template-str-negative-count-workflows.md` then published the exact four `str` negative-count correctness rows on `conditional-group-exists-replacement-template-workflows`;
  - `benchmarks/workloads/conditional_group_exists_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` still carry only the matching bytes negative-count benchmark rows in this run, so the adjacent `str` catch-up is the smallest surviving same-family slice; and
  - the existing benchmark owner path is already live with `100` measured workloads and `0` known gaps in the current checkout, so no implementation prerequisite blocks this benchmark publication.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync` returned `4 passed, 56 subtests passed` in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-template-str-negative-count-bench.py` completed successfully with `100` measured workloads and `0` known gaps in this run.

## Completion
- Added the four bounded `str count=-1` template workloads on the existing `conditional-group-exists-boundary` manifest and extended the shared combined-boundary benchmark assertions so the template slice, representative measured rows, and round-trip payload checks cover the new `str` negative-count rows alongside the already-landed bytes rows.
- Regenerated the tracked benchmark publication at `reports/benchmarks/latest.py`; the tracked summary now reports `1035/1035` measured workloads with `known_gap_count == 0`, and the tracked `conditional-group-exists-boundary` manifest summary now reports `104` measured workloads with `0` known gaps.
- Verification completed with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync` -> `4 passed, 64 subtests passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1155-conditional-template-negative-count-str.py` -> `104/104` measured, `0` known gaps.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` -> `1035/1035` measured, `0` known gaps.
