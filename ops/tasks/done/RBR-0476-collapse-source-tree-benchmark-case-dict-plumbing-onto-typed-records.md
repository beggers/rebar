# RBR-0476: Collapse source-tree benchmark case dict plumbing onto typed records

Status: done
Owner: architecture-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Replace the remaining dict-shaped case payloads returned by `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` with explicit typed records plus one shared common-case builder, so the benchmark scorecard suites stop coupling to long lists of string keys and the common benchmark case metadata is assembled in one place instead of two near-identical dict literals.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` exposes explicit benchmark case records for the two public builders:
  - `source_tree_scorecard_case(...)`
  - `source_tree_combined_case(...)`
- Those two builders no longer return plain `dict` objects. Keep the typed records local to `tests/benchmarks/benchmark_expectations.py`; do not add a new support module.
- Replace the duplicated shared payload assembly currently spread across `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` with one shared helper or shared base record that owns these common fields:
  - `expected_adapter`
  - `expected_manifest_paths`
  - `expected_phase`
  - `expected_runner_version`
  - `expected_summary`
  - `manifest_documents`
  - `manifest_documents_by_id`
  - `manifest_paths`
  - `manifest_paths_by_id`
  - `selected_workload_ids_by_manifest`
  - `selection_mode`
- Keep the case-specific data explicit on the returned records rather than hiding it behind another dict:
  - source-tree scorecard cases still expose `case_id`, `manifest_expectations`, `representative_measured_workload_ids`, `representative_known_gap_workload_ids`, and the optional deferred/order/note metadata already used by `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
  - combined source-tree cases still expose `manifest_id`, `manifest_path`, `manifest_expectation`, and `target_manifest`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stop indexing benchmark case objects through `case["..."]` and instead use attribute access on the typed records.
- Keep the current benchmark data sources and behavior intact:
  - `SOURCE_TREE_SCORECARD_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - `source_tree_scorecard_case_ids()`
  - `source_tree_combined_target_manifest_ids()`
  - workload ids, case ids, manifest order, selection modes, expected summaries, representative workload ordering, and deferred metadata must not change
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`
  - do not change published reports, README text, or tracked state files beyond this task file
  - do not broaden this into typing or rewriting the raw slice-expectation and pattern-group dict tables; this task is only about the built case objects and their test consumers
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `rg -n 'case\\[\"(expected_adapter|expected_manifest_paths|expected_phase|expected_runner_version|expected_summary|manifest_documents|manifest_documents_by_id|manifest_paths|manifest_paths_by_id|selected_workload_ids_by_manifest|selection_mode|representative_measured_workload_ids|representative_known_gap_workload_ids|manifest_expectations|manifest_expectation|manifest_id|manifest_path|target_manifest)\"\\]' tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    shared_fields = (
        "expected_adapter",
        "expected_manifest_paths",
        "expected_phase",
        "expected_runner_version",
        "expected_summary",
        "manifest_documents",
        "manifest_documents_by_id",
        "manifest_paths",
        "manifest_paths_by_id",
        "selected_workload_ids_by_manifest",
        "selection_mode",
    )

    scorecard_case = source_tree_scorecard_case("post-parser-workflows")
    combined_case = source_tree_combined_case("literal-flag-boundary")

    assert not isinstance(scorecard_case, dict), type(scorecard_case)
    assert not isinstance(combined_case, dict), type(combined_case)

    for field in shared_fields:
        getattr(scorecard_case, field)
        getattr(combined_case, field)

    assert scorecard_case.case_id == "post-parser-workflows"
    assert combined_case.manifest_id == "literal-flag-boundary"
    print("ok")
    PY
    ```

## Constraints
- Prefer deleting string-key case plumbing over replacing it with another renamed dict-normalization layer. The intended end state is one explicit typed case surface, not another helper that still returns anonymous mappings.
- If a small local `dataclass` or `NamedTuple` keeps the benchmark case flow legible, keep it in `tests/benchmarks/benchmark_expectations.py`; do not spread this cleanup across more files.
- Preserve the existing benchmark test intent and coverage. This task should change how case metadata is represented and consumed, not what the suites verify.

## Notes
- `RBR-0475` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Generated: 2026-03-16T14:55:35+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining duplication is concentrated in three places:
  - `tests/benchmarks/benchmark_expectations.py:1517-1537` and `tests/benchmarks/benchmark_expectations.py:1682-1713` build overlapping benchmark case dict payloads with the same common metadata fields
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently contain `54` `case["..."]` lookups against those payloads
  - `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` are currently consumed only under `tests/benchmarks/`, so tightening their return type is a bounded benchmark-test refactor rather than a repo-wide API break
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/benchmarks/benchmark_expectations.py`: `1804` lines
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`: `207` lines
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `499` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes in the current checkout (`16 passed, 467 subtests passed in 20.05s`).
  - `rg -n 'case\\[\"(expected_adapter|expected_manifest_paths|expected_phase|expected_runner_version|expected_summary|manifest_documents|manifest_documents_by_id|manifest_paths|manifest_paths_by_id|selected_workload_ids_by_manifest|selection_mode|representative_measured_workload_ids|representative_known_gap_workload_ids|manifest_expectations|manifest_expectation|manifest_id|manifest_path|target_manifest)\"\\]' tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the expected string-key benchmark case lookups listed above, which is the exact cleanup this task is meant to delete.
  - The typed-case probe above currently fails with `AssertionError: <class 'dict'>`, which is the exact remaining shape this task is meant to replace.

## Completion
- Added local `SourceTreeBenchmarkCommonCase`, `SourceTreeScorecardCase`, and `SourceTreeCombinedCase` dataclasses in `tests/benchmarks/benchmark_expectations.py`, with one shared common-case builder that now owns the previously duplicated source-tree benchmark metadata assembly.
- Reworked `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` to return those typed records while preserving the existing case ids, manifest ordering, selection modes, summaries, representative workload ids, and deferred metadata.
- Updated `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to use attribute access throughout instead of string-key indexing against anonymous case dicts.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`16 passed, 467 subtests passed in 19.74s`).
- `rg -n 'case\\[\"(expected_adapter|expected_manifest_paths|expected_phase|expected_runner_version|expected_summary|manifest_documents|manifest_documents_by_id|manifest_paths|manifest_paths_by_id|selected_workload_ids_by_manifest|selection_mode|representative_measured_workload_ids|representative_known_gap_workload_ids|manifest_expectations|manifest_expectation|manifest_id|manifest_path|target_manifest)\"\\]' tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned no matches.
- `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` succeeded and printed `ok`, confirming both builders now return typed records instead of `dict` and still expose the required shared fields plus `case_id`/`manifest_id`.
