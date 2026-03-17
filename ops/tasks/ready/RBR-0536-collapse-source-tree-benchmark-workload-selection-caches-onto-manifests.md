# RBR-0536: Collapse source-tree benchmark workload-selection caches onto manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining per-manifest workload-id cache tables from the typed source-tree benchmark case records in `tests/benchmarks/benchmark_expectations.py` so those cases keep the loaded `BenchmarkManifest` objects plus only the minimum selection metadata they still need, instead of storing duplicate workload-id tuples that can already be derived from `manifest.workloads`.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` collapses the source-tree case selection cache onto manifests:
  - `SourceTreeBenchmarkCommonCase` no longer stores `selected_workload_ids_by_manifest`;
  - the case surface keeps or adds one minimal helper named `selected_workload_ids_for_manifest(manifest_id)` that derives per-manifest workload ids from `BenchmarkManifest.workloads` plus the case's smaller selection metadata instead of reading a prebuilt dict;
  - `_selected_workload_ids_by_manifest(...)` is removed;
  - `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` stop materializing per-manifest id tables for full cases; and
  - `expected_summary_for_manifests(...)` and `_source_tree_manifest_known_gap_counts(...)` accept the smaller selection representation without changing manifest order, selection mode, or summary totals.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` derive selected ids through `case.selected_workload_ids_for_manifest(...)` instead of reading `case.selected_workload_ids_by_manifest[...]`.
- Preserve current benchmark behavior exactly:
  - `source_tree_scorecard_case("compile-smoke")` still selects only `compile-literal-cold` and `compile-character-class-warm`;
  - `source_tree_scorecard_case("post-parser-workflows")` still selects all 8 `module-boundary` workloads in manifest order; and
  - `source_tree_combined_case("literal-flag-boundary")` still selects all 5 `regression-matrix` workloads in manifest order.
- Do not change manifest order, selected manifest sets, known-gap counts, representative workloads, scorecard payloads, or files under `benchmarks/workloads/`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    compile_smoke = source_tree_scorecard_case("compile-smoke")
    assert compile_smoke.selected_workload_ids_for_manifest("compile-smoke") == (
        "compile-literal-cold",
        "compile-character-class-warm",
    )

    post_parser = source_tree_scorecard_case("post-parser-workflows")
    assert post_parser.selected_workload_ids_for_manifest("module-boundary") == tuple(
        workload.workload_id
        for workload in post_parser.manifest_for_id("module-boundary").workloads
    )

    combined = source_tree_combined_case("literal-flag-boundary")
    assert combined.selected_workload_ids_for_manifest("regression-matrix") == tuple(
        workload.workload_id
        for workload in combined.manifest_for_id("regression-matrix").workloads
    )
    print("ok")
    PY
    ```
  - `rg -n "selected_workload_ids_by_manifest" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not broaden it into manifest-selector rewrites, scorecard assertion redesign, benchmark workload edits, or feature/parity work.
- Prefer storing one smaller case-level selection representation plus a derivation helper over introducing another per-manifest cache layer or another wrapper type.
- Preserve the current source-tree case ids, manifest ids, and helper names other than the deleted cache field.

## Notes
- `RBR-0535` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0536` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The duplicate surface is concrete and still live in the current checkout:
  - `rg -n "selected_workload_ids_by_manifest" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the case field, the builder helper, and the direct test call sites this task is meant to delete;
  - `source_tree_scorecard_case("compile-smoke")` currently stores `{'compile-smoke': ('compile-literal-cold', 'compile-character-class-warm')}` in that cache; and
  - the same cache currently duplicates full-manifest selections that are already present on the manifest objects, including 8 `module-boundary` workload ids in `source_tree_scorecard_case("post-parser-workflows")` and 5 `regression-matrix` workload ids in `source_tree_combined_case("literal-flag-boundary")`.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`46 passed, 1423 subtests passed in 21.56s`).
  - The inline `selected_workload_ids_for_manifest(...)` probe in this task currently fails with `AttributeError: 'SourceTreeScorecardCase' object has no attribute 'selected_workload_ids_for_manifest'`, which is the exact missing helper this cleanup is meant to add while deleting the old cache field.
