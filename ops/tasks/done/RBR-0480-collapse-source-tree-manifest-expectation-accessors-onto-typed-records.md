# RBR-0480: Collapse source-tree manifest expectation accessors onto typed records

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining dict-shaped public manifest expectation payloads in the source-tree benchmark expectation layer with explicit typed records, so the scorecard suites stop carrying string-key coupling for known-gap and representative-id metadata and the benchmark case API becomes uniformly attribute-based.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` exposes explicit typed records for the remaining public manifest expectation surfaces:
  - `SourceTreeCombinedCase.manifest_expectation`
  - `SourceTreeScorecardCase.manifest_expectations[...]`
- Those public manifest expectation surfaces no longer expose plain `dict` objects. Keep the typed records local to `tests/benchmarks/benchmark_expectations.py`; do not add a new support module.
- The typed manifest expectation surface covers the fields currently read through string keys:
  - `known_gap_count`
  - `representative_measured_workload_ids`
  - `representative_known_gap_workload_ids`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stop indexing manifest expectations through string keys and instead use attribute access on the typed records.
- Preserve the current benchmark data and queue-facing behavior exactly:
  - keep `SOURCE_TREE_SCORECARD_EXPECTATIONS`, `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, and `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` as the canonical expectation data sources in this module;
  - keep the current case ids returned by `source_tree_scorecard_case_ids()` and target manifest ids returned by `source_tree_combined_target_manifest_ids()`;
  - keep the current known-gap counts, representative measured workload ids, and representative known-gap workload ids unchanged.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change published reports, README text, or tracked state files beyond this task file;
  - do not broaden this into fixing the unrelated combined benchmark summary drift currently queued as feature work in `RBR-0479`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_full_scorecard_cases_derive_known_gap_counts_from_manifest_inventories tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_post_parser_workflows_promote_ignorecase_ascii_pair_to_measured_representatives tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_regression_pack_full_promotes_bytes_backreference_probe_to_measured tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_single_manifest_scorecards_keep_slice_backed_representatives`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_manifest_gap_inventories_derive_public_known_gap_counts tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_default_public_manifest_expectations_restore_empty_representative_ids tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_shape_backed_manifests_keep_derived_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_regression_manifest_is_fully_measured_on_the_shared_surface tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_scoped_manifests_keep_slice_backed_representatives`
  - `rg -n 'manifest_expectation\\["(known_gap_count|representative_measured_workload_ids|representative_known_gap_workload_ids)"\\]|manifest_expectations\\[[^]]+\\]\\["known_gap_count"\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.
  - `rg -n 'manifest_expectations: dict\\[str, dict\\[str, int\\]\\]|manifest_expectation: dict\\[str, Any\\]' tests/benchmarks/benchmark_expectations.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    combined_case = source_tree_combined_case("pattern-boundary")
    scorecard_case = source_tree_scorecard_case("post-parser-workflows")

    combined_expectation = combined_case.manifest_expectation
    scorecard_expectation = scorecard_case.manifest_expectations["literal-flag-boundary"]

    assert not isinstance(combined_expectation, dict), type(combined_expectation)
    assert not isinstance(scorecard_expectation, dict), type(scorecard_expectation)

    assert combined_expectation.known_gap_count == 0
    assert combined_expectation.representative_measured_workload_ids == ()
    assert combined_expectation.representative_known_gap_workload_ids == ()
    assert scorecard_expectation.known_gap_count == 0
    print("ok")
    PY
    ```

## Constraints
- Prefer a small local dataclass or `NamedTuple` expectation surface over another renamed dict-normalization layer. The intended end state is one explicit typed manifest expectation API, not a second helper that still returns anonymous mappings.
- If the implementation keeps the raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` table dict-shaped for brevity, keep that raw store local and convert it once at the public boundary; do not add another registry module or spread this cleanup across more files.
- Preserve the current benchmark test intent and representative-coverage assertions. This task should change how manifest expectation metadata is represented and consumed, not what the suites verify.

## Notes
- `RBR-0479` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Generated: 2026-03-16T16:25:07+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining public manifest-expectation coupling is concentrated in three places:
  - `tests/benchmarks/benchmark_expectations.py` still types `SourceTreeScorecardCase.manifest_expectations` and `SourceTreeCombinedCase.manifest_expectation` as dict payloads.
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently contain `15` string-key manifest-expectation lookups.
  - The public manifest-expectation probe above currently prints `dict` / `dict`, which is the exact shape this task is meant to replace.
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/benchmarks/benchmark_expectations.py`: `2133` lines
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`: `208` lines
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `496` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_full_scorecard_cases_derive_known_gap_counts_from_manifest_inventories tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_post_parser_workflows_promote_ignorecase_ascii_pair_to_measured_representatives tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_regression_pack_full_promotes_bytes_backreference_probe_to_measured tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_single_manifest_scorecards_keep_slice_backed_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_manifest_gap_inventories_derive_public_known_gap_counts tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_default_public_manifest_expectations_restore_empty_representative_ids tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_shape_backed_manifests_keep_derived_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_regression_manifest_is_fully_measured_on_the_shared_surface tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_scoped_manifests_keep_slice_backed_representatives` passes in the current checkout (`11 passed, 23 subtests passed in 0.59s`).
  - `rg -n 'manifest_expectation\\["(known_gap_count|representative_measured_workload_ids|representative_known_gap_workload_ids)"\\]|manifest_expectations\\[[^]]+\\]\\["known_gap_count"\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns `15` matches, which is the exact string-key manifest-expectation plumbing this task should delete rather than rename.
  - The public manifest-expectation probe above currently reports `dict` / `dict`, which is the exact remaining shape this task is meant to replace.
  - The broad combined benchmark regression is currently red for unrelated feature drift and should stay out of this task's acceptance surface: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently fails with `24` summary mismatches because the ready `RBR-0479` benchmark catch-up has not landed yet.

## Completion
- 2026-03-16: Added a local `SourceTreeManifestExpectation` dataclass in `tests/benchmarks/benchmark_expectations.py` and converted the public `SourceTreeCombinedCase.manifest_expectation` plus `SourceTreeScorecardCase.manifest_expectations[...]` surfaces to typed records while keeping the raw manifest tables dict-shaped and unchanged.
- 2026-03-16: Rewired the scorecard and combined benchmark suites to read manifest expectation metadata through attributes instead of string keys, preserving the existing known-gap counts and representative workload ids.
- 2026-03-16: Verified with the task's targeted pytest command (`11 passed, 23 subtests passed in 0.60s`), both required `rg -n ...` checks (no matches), and the public typed-record probe (`ok`).
