# RBR-0541: Collapse source-tree benchmark path wrappers onto cached manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the leftover path-to-id wrapper layer in `tests/benchmarks/benchmark_expectations.py` now that the source-tree scorecard and combined-case builders already run on cached `BenchmarkManifest` objects. The intended end state is one cached manifest path, with published selector order and case path lists derived directly from those typed records instead of dead or single-use path wrapper helpers.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` deletes the remaining source-tree path-wrapper leftovers:
  - `_published_source_tree_manifests()` no longer round-trips `_published_full_suite_manifest_paths()` through `manifest_id_for_path(...)` before looking records back up in `_source_tree_manifest_records()`;
  - `manifest_id_for_path(...)` is removed;
  - `manifest_path_for_id(...)` is removed; and
  - `selected_manifest_paths_for_target_manifest(...)` is removed.
- The cached-manifest path stays behaviorally identical for the existing public helpers:
  - `source_tree_scorecard_case("post-parser-workflows").manifest_paths` still yields, in order, `module_boundary.py`, `collection_replacement_boundary.py`, and `literal_flag_boundary.py`;
  - `source_tree_combined_case("literal-flag-boundary").manifest_paths` still yields, in order, `compile_matrix.py`, `module_boundary.py`, `pattern_boundary.py`, `collection_replacement_boundary.py`, `literal_flag_boundary.py`, and `regression_matrix.py`; and
  - the corresponding `relative_manifest_paths` values still remain repo-relative strings for the same ordered path sets.
- Preserve current source-tree benchmark behavior exactly:
  - do not change `relative_manifest_path(...)`;
  - do not change compile-smoke or published-full-suite selector ordering;
  - do not change regression-manifest append behavior for combined cases;
  - do not change manifest ids, selected workload ids, representative workload ids, known-gap counts, or scorecard payload expectations; and
  - do not touch files under `benchmarks/workloads/`, `python/rebar_harness/`, or published reports.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    scorecard_case = source_tree_scorecard_case("post-parser-workflows")
    combined_case = source_tree_combined_case("literal-flag-boundary")

    assert [path.name for path in scorecard_case.manifest_paths] == [
        "module_boundary.py",
        "collection_replacement_boundary.py",
        "literal_flag_boundary.py",
    ]
    assert [path.name for path in combined_case.manifest_paths] == [
        "compile_matrix.py",
        "module_boundary.py",
        "pattern_boundary.py",
        "collection_replacement_boundary.py",
        "literal_flag_boundary.py",
        "regression_matrix.py",
    ]
    print("ok")
    PY
    ```
  - `rg -n "def (manifest_id_for_path|manifest_path_for_id|selected_manifest_paths_for_target_manifest)\\(" tests/benchmarks/benchmark_expectations.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not broaden it into benchmark-anchor contract cleanup, selector redesign, manifest registry rewrites, or feature/parity work.
- Prefer deleting the dead path helpers over adding another path cache or another manifest-selection abstraction.
- Keep the existing `SourceTreeBenchmarkCommonCase` surface intact other than the deleted internal wrapper helpers that no longer have useful callers.

## Notes
- `RBR-0540` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0541` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The leftover wrapper surface is concrete in the current checkout:
  - `rg -n "manifest_id_for_path\\(|manifest_path_for_id\\(|selected_manifest_paths_for_target_manifest\\(" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` currently returns only one internal round-trip use plus three function definitions, all in `tests/benchmarks/benchmark_expectations.py`;
  - `manifest_path_for_id(...)` and `selected_manifest_paths_for_target_manifest(...)` currently have no call sites in the source-tree benchmark expectation/test surface; and
  - `manifest_id_for_path(...)` is currently used only once, inside `_published_source_tree_manifests()`, to map already-selected published paths back into cached `BenchmarkManifest` records.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`47 passed, 1449 subtests passed in 21.58s`).
  - The inline manifest-path probe in this task prints `ok`.
