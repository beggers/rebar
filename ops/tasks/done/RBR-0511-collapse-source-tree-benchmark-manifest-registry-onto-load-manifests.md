# RBR-0511: Collapse the source-tree benchmark manifest registry onto `load_manifests(...)`

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining duplicate path-plus-manifest registry in `tests/benchmarks/benchmark_expectations.py` so the source-tree benchmark expectation layer stops storing `pathlib.Path` beside `BenchmarkManifest` even though `BenchmarkManifest.path` already owns that path, and stops rebuilding that inventory through per-file `load_manifest(...)` calls. The intended end state is one cached typed manifest inventory loaded through `load_manifests(...)`, with path/id helpers deriving from `manifest.path` and current scorecard behavior unchanged.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` collapses its cached source-tree manifest registry onto the existing bulk loader:
  - `_source_tree_manifest_records()` (or the helper that replaces it) loads the compile-smoke manifest plus the published full-suite selector through one `load_manifests(...)` call instead of looping those paths and calling `load_manifest(path)` one file at a time.
  - The cached inventory stores `BenchmarkManifest` records directly, not `tuple[pathlib.Path, BenchmarkManifest]` values.
  - `manifest_id_for_path(...)` and `manifest_path_for_id(...)` derive their answers from `BenchmarkManifest.path` on the cached typed records rather than a parallel stored `path` tuple slot.
  - `source_tree_scorecard_case(...)`, `source_tree_combined_target_manifest_ids()`, and `selected_manifest_paths_for_target_manifest(...)` preserve the current manifest ordering, regression-manifest append behavior, and selector drift checks for the same compile-smoke and published full-suite selections.
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` stops preloading published manifest ids through repeated single-file loads:
  - the selector-order and uniqueness test derives `expected_manifest_ids` from one `load_manifests(list(published_manifest_paths))` call instead of first looping `load_manifest(path).manifest_id` and then loading the same paths again;
  - manifest-id uniqueness, workload-id uniqueness, and per-manifest workload-presence assertions remain unchanged; and
  - the contract still proves the published selector excludes `compile_smoke.py` and the built-native smoke selector stays a subset of the published full-suite selector.
- Preserve current benchmark expectation behavior exactly:
  - keep compile-smoke path resolution unchanged;
  - keep `source_tree_scorecard_case("post-parser-workflows")` starting with the `module-boundary` manifest;
  - keep `source_tree_combined_target_manifest_ids()` starting with `module-boundary`; and
  - do not change benchmark workload manifests, manifest selectors in `python/rebar_harness/benchmarks.py`, report payloads, or the source-tree benchmark expectation tables beyond this structural cleanup.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        manifest_path_for_id,
        source_tree_combined_target_manifest_ids,
        source_tree_scorecard_case,
    )

    case = source_tree_scorecard_case("post-parser-workflows")
    assert case.manifests[0].manifest_id == "module-boundary"
    assert manifest_path_for_id("compile-smoke").name == "compile_smoke.py"
    assert source_tree_combined_target_manifest_ids()[0] == "module-boundary"
    print("ok")
    PY
    ```
  - `rg -n 'dict\\[str, tuple\\[pathlib\\.Path, BenchmarkManifest\\]\\]|for path in \\(_compile_smoke_manifest_path\\(\\), \\*_published_full_suite_manifest_paths\\(\\)\\)|load_manifest\\(path\\)' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change files under `benchmarks/workloads/`, do not change `python/rebar_harness/benchmarks.py`, do not change published benchmark reports, and do not touch README or tracked state files.
- Prefer the existing `load_manifests(...)` bulk loader and `BenchmarkManifest.path` over adding another manifest-registry helper module, compatibility wrapper, or duplicated cached path table.
- Do not broaden this task into benchmark anchor-contract cleanup, source-tree expectation-table redesign, or feature/frontier work already reserved as `RBR-0510`.

## Notes
- `RBR-0510` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so this architecture cleanup starts at `RBR-0511`.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in the live filesystem before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false` and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining duplicate surface is concrete rather than speculative:
  - `rg -n 'load_manifest\\((path|manifest_path)\\)|for path in \\(_compile_smoke_manifest_path\\(\\), \\*_published_full_suite_manifest_paths\\(\\)\\)|dict\\[str, tuple\\[pathlib\\.Path, BenchmarkManifest\\]\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py -g '*.py'` currently returns three matches across exactly these two files.
  - `tests/benchmarks/benchmark_expectations.py` still caches `dict[str, tuple[pathlib.Path, BenchmarkManifest]]` records and loads each manifest individually, while `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` still calls `load_manifest(path).manifest_id` before bulk-loading the same published selector.
- 2026-03-17 architecture probes from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`31 passed, 1145 subtests passed in 21.01s`).
  - The inline probe above currently prints `ok`.

## Completion Notes
- Collapsed `tests/benchmarks/benchmark_expectations.py::_source_tree_manifest_records()` onto one cached `load_manifests([...])` call covering `compile_smoke.py` plus the published full-suite selector, so the cached registry now stores `BenchmarkManifest` objects directly and derives ids and paths from `manifest.path`.
- Preserved the existing source-tree benchmark ordering behavior: `manifest_id_for_path(...)` and `manifest_path_for_id(...)` now resolve through `BenchmarkManifest.path`, while `source_tree_scorecard_case("post-parser-workflows")`, `source_tree_combined_target_manifest_ids()`, and `selected_manifest_paths_for_target_manifest(...)` continue to run through the same selector order and regression-manifest append flow.
- Updated `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` so the published full-suite inventory test bulk-loads manifests once, verifies that `load_manifests(...)` preserves selector order via `manifest.path`, and keeps the manifest-id uniqueness, workload-id uniqueness, workload-presence, compile-smoke exclusion, and built-native-subset assertions intact.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline `source_tree_scorecard_case(...)` / `manifest_path_for_id(...)` / `source_tree_combined_target_manifest_ids()` probe (`ok`), and `rg -n 'dict\\[str, tuple\\[pathlib\\.Path, BenchmarkManifest\\]\\]|for path in \\(_compile_smoke_manifest_path\\(\\), \\*_published_full_suite_manifest_paths\\(\\)\\)|load_manifest\\(path\\)' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`, which now returns no matches.
