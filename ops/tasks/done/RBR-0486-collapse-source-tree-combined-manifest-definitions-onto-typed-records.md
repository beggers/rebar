# RBR-0486: Collapse source-tree combined manifest definitions onto typed records

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining dict-shaped source-tree combined-manifest expectation definitions with an explicit typed record so the benchmark expectation layer stops carrying raw string-key manifest plumbing and the combined benchmark suite stops reaching into dict entries directly.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` exposes an explicit typed record for the per-manifest source-tree combined definition surface:
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]`
- That definition surface no longer exposes plain `dict` objects. Keep the typed record local to `tests/benchmarks/benchmark_expectations.py`; do not add a new support module.
- The typed manifest-definition surface covers the currently stored optional metadata:
  - `known_gap_workload_ids`
  - `representative_measured_workload_ids`
  - `representative_known_gap_workload_ids`
  - `shape_expectation`
- Preserve the lean-table contract from `RBR-0458` and `RBR-0469`: manifests without an explicit stored override do not grow synthetic empty tuples. Represent missing stored metadata distinctly (for example with `None`) so callers can still distinguish "no explicit override" from "explicit empty tuple" when deriving slice-backed representatives and shape-backed coverage.
- If a manifest carries `shape_expectation`, that stored value is itself typed. Reuse the existing typed shape and pattern-group records if practical. `source_tree_combined_manifest_shape_expectation(...)` should stop rebuilding those objects from raw dicts and instead return the stored typed expectation.
- `_source_tree_manifest_expectation_workload_ids(...)` disappears, and the source-tree combined-manifest helper path stops indexing definition payloads through string keys or membership checks. Preserve current behavior while converting these helpers to attribute access against the typed definition surface:
  - `source_tree_combined_manifest_representative_measured_workload_ids(...)`
  - `_source_tree_manifest_known_gap_count(...)`
  - `_source_tree_manifest_representative_measured_workload_ids(...)`
  - `_source_tree_manifest_representative_known_gap_workload_ids(...)`
  - `_public_source_tree_manifest_expectation(...)`
  - `_source_tree_manifest_known_gap_counts(...)`
  - `source_tree_scorecard_case(...)`
  - `expected_summary_for_manifests(...)`
  - `representative_measured_workload_ids(...)`
  - `source_tree_combined_manifest_shape_expectation(...)`
  - `source_tree_combined_slice_derived_manifest_ids(...)`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops asserting against raw manifest-definition dicts and instead checks the typed registry surface through attributes and optional fields.
- Preserve the current benchmark behavior exactly:
  - keep the manifest ids in `source_tree_combined_target_manifest_ids()` unchanged;
  - keep the manifest ids in `source_tree_combined_slice_derived_manifest_ids()` unchanged;
  - keep the current known-gap counts, representative measured workload ids, representative known-gap workload ids, and shape-backed representative coverage unchanged for every tracked manifest; and
  - keep `SourceTreeCombinedCase.manifest_expectation` and `SourceTreeScorecardCase.manifest_expectations[...]` unchanged as the already-typed public expectation surfaces from `RBR-0480`.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change published reports, README text, or tracked state files beyond this task file; and
  - do not broaden this into the ready benchmark catch-up feature work in `RBR-0485`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_raw_manifest_expectations_omit_empty_measured_representative_defaults tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_manifest_gap_inventories_derive_public_known_gap_counts tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_default_public_manifest_expectations_restore_empty_representative_ids tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_shape_backed_manifests_keep_derived_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_regression_manifest_is_fully_measured_on_the_shared_surface tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_scoped_manifests_keep_slice_backed_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite`
  - `rg -n '\\.get\\("(known_gap_workload_ids|representative_measured_workload_ids|representative_known_gap_workload_ids|shape_expectation)"\\)|\\["(known_gap_workload_ids|representative_measured_workload_ids|representative_known_gap_workload_ids|shape_expectation)"\\]|"representative_measured_workload_ids"\\s+not in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS\\[manifest_id\\]|"shape_expectation"\\s+not in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS\\[manifest_id\\]|def _source_tree_manifest_expectation_workload_ids\\(|raw_expectation: dict\\[str, Any\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS,
        source_tree_combined_case,
        source_tree_combined_manifest_shape_expectation,
    )

    manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS["pattern-boundary"]
    assert not isinstance(manifest_definition, dict), type(manifest_definition)
    assert manifest_definition.representative_measured_workload_ids is None
    assert manifest_definition.shape_expectation is not None

    wider_range_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
        "wider-ranged-repeat-quantified-group-boundary"
    ]
    assert not isinstance(wider_range_definition.shape_expectation, dict), type(
        wider_range_definition.shape_expectation
    )
    assert wider_range_definition.shape_expectation.pattern_groups
    assert (
        source_tree_combined_manifest_shape_expectation(
            "wider-ranged-repeat-quantified-group-boundary"
        )
        == wider_range_definition.shape_expectation
    )

    case = source_tree_combined_case("grouped-named-boundary")
    assert case.manifest_expectation.representative_measured_workload_ids == (
        "module-search-grouped-segment-cold-gap",
        "pattern-search-grouped-segment-warm-gap",
    )
    print("ok")
    PY
    ```

## Constraints
- Prefer one small local dataclass or `NamedTuple` manifest-definition surface over another renamed raw-dict normalization helper. The intended end state is one explicit typed manifest-definition API, not a second helper that still routes everything through string keys.
- If you keep a raw staging table for brevity, keep it private and convert it exactly once at the `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]` boundary; do not leave the exported registry or its consumers coupled to dict lookups.
- Do not broaden this task into typing `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, source-tree scorecard case definitions, benchmark manifest documents, or the ready `numbered-backreference-boundary` feature catch-up in `RBR-0485`.

## Notes
- `RBR-0485` is already queued as the ready-head feature task, and the runtime dashboard is clean (`Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0486` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the current task queue, so it is the next available architecture id.
- The remaining raw combined-manifest definition coupling is concentrated in two active files:
  - `tests/benchmarks/benchmark_expectations.py` still stores `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]` as dict payloads, still carries `_source_tree_manifest_expectation_workload_ids(...)`, and still rebuilds `shape_expectation` from raw dicts.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still reaches into the raw registry through `.get("representative_measured_workload_ids")`, `["known_gap_workload_ids"]`, and `["representative_measured_workload_ids"]`.
- Current file sizes underline why this is still a worthwhile bounded simplification:
  - `tests/benchmarks/benchmark_expectations.py`: `2097` lines
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `553` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_raw_manifest_expectations_omit_empty_measured_representative_defaults tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_manifest_gap_inventories_derive_public_known_gap_counts tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_zero_default_public_manifest_expectations_restore_empty_representative_ids tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_shape_backed_manifests_keep_derived_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_regression_manifest_is_fully_measured_on_the_shared_surface tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_scoped_manifests_keep_slice_backed_representatives tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite` passes in the current checkout (`17 passed, 204 subtests passed in 2.46s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is currently red for unrelated ready-queue feature drift because `RBR-0485` has not landed yet (`23 failed, 12 passed, 327 subtests passed`), so the acceptance surface above deliberately excludes `test_runner_regenerates_combined_source_tree_boundary_scorecards`.
  - `rg -n '\\.get\\("(known_gap_workload_ids|representative_measured_workload_ids|representative_known_gap_workload_ids|shape_expectation)"\\)|\\["(known_gap_workload_ids|representative_measured_workload_ids|representative_known_gap_workload_ids|shape_expectation)"\\]|"representative_measured_workload_ids"\\s+not in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS\\[manifest_id\\]|"shape_expectation"\\s+not in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS\\[manifest_id\\]|def _source_tree_manifest_expectation_workload_ids\\(|raw_expectation: dict\\[str, Any\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the raw-key and raw-helper matches called out above, which is the exact coupling this task should delete rather than rename.
  - The typed-registry probe above currently fails immediately with `AssertionError: <class 'dict'>`, which is the exact public-shape cleanup this task is meant to complete.

## Completion Note
- 2026-03-16 architecture-implementation: Replaced `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` with a typed manifest-definition dataclass, stored typed shape expectations directly in the registry, removed `_source_tree_manifest_expectation_workload_ids(...)`, converted the combined-manifest helper path to attribute access, and updated the combined benchmark tests to assert against the typed optional fields instead of raw dict keys. Verified with the pinned pytest command (`17 passed, 204 subtests passed`), the no-match `rg` check, and the typed-registry probe (`ok`).
