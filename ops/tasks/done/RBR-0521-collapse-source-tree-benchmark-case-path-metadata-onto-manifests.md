# RBR-0521: Collapse source-tree benchmark case path metadata onto manifests

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining duplicate manifest-path metadata from the source-tree benchmark case records in `tests/benchmarks/benchmark_expectations.py` so those cases stop caching path lists and relative-path strings that are already derivable from the loaded `BenchmarkManifest.path` fields. The intended end state is that source-tree benchmark cases keep the typed manifest inventory plus selection metadata, while tests derive runtime path lists and relative path assertions directly from the manifests they already hold.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` collapses source-tree benchmark case path metadata onto the existing typed manifest records:
  - `SourceTreeBenchmarkCommonCase` no longer stores `expected_manifest_paths`, `manifest_paths`, or `manifest_paths_by_id`;
  - `SourceTreeCombinedCase` no longer stores a duplicate `manifest_path` string;
  - `_build_source_tree_benchmark_common_case(...)` and `source_tree_combined_case(...)` stop assembling those duplicate path caches and preserve the current manifest order, selection modes, expected summaries, and regression-manifest append behavior; and
  - `manifest_id_for_path(...)`, `manifest_path_for_id(...)`, `relative_manifest_path(...)`, `source_tree_scorecard_case(...)`, `source_tree_combined_case(...)`, and `selected_manifest_paths_for_target_manifest(...)` keep their current external behavior aside from the deleted duplicate case fields.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` derives path inputs and relative-path expectations directly from `case.manifests` instead of case-level cached path fields:
  - `run_source_tree_benchmark_scorecard(...)` receives the ordered `BenchmarkManifest.path` list derived from `case.manifests`;
  - `assert_source_tree_benchmark_contract(...)` receives relative paths derived from `manifest.path`; and
  - per-manifest assertions derive the manifest path string from `case.manifests_by_id[manifest_id].path` instead of `case.manifest_paths_by_id[manifest_id]`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` does the same for combined source-tree cases:
  - combined scorecard runs use the ordered `BenchmarkManifest.path` list derived from `case.manifests`;
  - artifact-path assertions derive their expected relative paths from `case.manifests`; and
  - per-manifest assertions derive the target manifest path string from `case.target_manifest.path` instead of `case.manifest_path`.
- Preserve current benchmark behavior exactly:
  - do not change files under `benchmarks/workloads/`;
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change published reports, README text, or tracked state files beyond this task file; and
  - do not broaden this into another manifest-registry rewrite, report-assertion redesign, benchmark-selector cleanup, or feature/parity work.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `rg -n "expected_manifest_paths: list\\[str\\]|manifest_paths: list\\[pathlib\\.Path\\]|manifest_paths_by_id: dict\\[str, str\\]|manifest_path: str|case\\.expected_manifest_paths\\b|case\\.manifest_paths\\b|case\\.manifest_paths_by_id\\b|case\\.manifest_path\\b" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        relative_manifest_path,
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    scorecard_case = source_tree_scorecard_case("post-parser-workflows")
    assert [relative_manifest_path(manifest.path) for manifest in scorecard_case.manifests] == [
        "benchmarks/workloads/module_boundary.py",
        "benchmarks/workloads/collection_replacement_boundary.py",
        "benchmarks/workloads/literal_flag_boundary.py",
    ]

    combined_case = source_tree_combined_case("literal-flag-boundary")
    assert relative_manifest_path(combined_case.target_manifest.path) == (
        "benchmarks/workloads/literal_flag_boundary.py"
    )
    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup structural only. The task should delete redundant case metadata, not change benchmark manifests, workload ids, scorecard payloads, or benchmark-selection semantics.
- Prefer deriving paths directly from `BenchmarkManifest.path` at the benchmark test call sites over introducing a new benchmark-case path wrapper or another cached path table.
- Treat this as a follow-on to the earlier typed-case and manifest-registry cleanups in `tests/benchmarks/benchmark_expectations.py`; do not reintroduce dict-shaped case payloads or per-path manifest registries.

## Notes
- `RBR-0520` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0521` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining duplicate surface is concrete and still live in the current checkout:
  - `tests/benchmarks/benchmark_expectations.py` still stores `expected_manifest_paths`, `manifest_paths`, `manifest_paths_by_id`, and `manifest_path` on the typed source-tree benchmark case records even though `BenchmarkManifest.path` already owns those paths;
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` still passes `case.manifest_paths`, `case.expected_manifest_paths`, and `case.manifest_paths_by_id[manifest_id]` into the scorecard runner and assertion helpers; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still passes `case.manifest_paths`, `case.expected_manifest_paths`, and `REPO_ROOT / case.manifest_path` into those same flows.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`37 passed, 1279 subtests passed in 21.98s`).
  - The inline `relative_manifest_path(...)` probe above currently prints `ok`.
  - `rg -n "expected_manifest_paths|manifest_paths_by_id|manifest_path: str|manifest_path=common_case\\.manifest_paths_by_id|REPO_ROOT / case\\.manifest_path|relative_manifest_path\\(" tests/benchmarks -g '*.py'` currently returns the duplicate case-path fields and call sites listed above, which is the exact cleanup this task is meant to delete.

## Completion Notes
- 2026-03-17: Removed the duplicate source-tree case path caches from `tests/benchmarks/benchmark_expectations.py` and updated the source-tree scorecard tests to derive runner inputs and artifact-path assertions directly from `BenchmarkManifest.path`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`37 passed, 1279 subtests passed in 21.89s`), the required `rg -n ...` acceptance grep returned no matches, and the inline `relative_manifest_path(...)` probe printed `ok`.
