# RBR-0531: Collapse source-tree benchmark case builders onto cached manifests

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining repeated benchmark manifest reloads from `tests/benchmarks/benchmark_expectations.py` so `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` reuse the cached typed source-tree manifest inventory they already depend on instead of reparsing the same Python manifest modules on every case build.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` routes source-tree case building through the cached inventory:
  - add or reuse helper(s) that return ordered `BenchmarkManifest` records from `_source_tree_manifest_records()` (or a minimally renamed equivalent) without calling `load_manifests(...)` again for the same source-tree subsets;
  - `source_tree_scorecard_case(...)` stops resolving manifest ids back to paths and then calling `load_manifests(manifest_paths)`;
  - `source_tree_combined_case(...)` stops taking `selected_manifest_paths_for_target_manifest(...)` output and then calling `load_manifests(list(manifest_paths))`; and
  - current manifest order and selection behavior stay unchanged:
    - `source_tree_scorecard_case("post-parser-workflows")` still yields `module-boundary`, `collection-replacement-boundary`, and `literal-flag-boundary` in that order;
    - `source_tree_combined_case("literal-flag-boundary")` still yields `compile-matrix`, `module-boundary`, `pattern-boundary`, `collection-replacement-boundary`, `literal-flag-boundary`, and `regression-matrix` in that order; and
    - `combined_case.target_manifest.manifest_id` remains `"literal-flag-boundary"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` adds or updates one contract that proves the source-tree case builders now reuse the cached inventory rather than reparsing manifests for each case build:
  - the contract may assert shared manifest object identity or another direct cache-backed invariant across `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)`; and
  - keep the existing scorecard summary, manifest-contract, deferred-work, and representative-workload checks intact.
- Preserve current benchmark behavior exactly:
  - do not change files under `benchmarks/workloads/`;
  - do not change `python/rebar_harness/benchmarks.py`, manifest selectors, scorecard payloads, or published reports;
  - do not change `selected_manifest_paths_for_target_manifest(...)`, regression-manifest append behavior, or `relative_manifest_path(...)` call sites except where a minimal cache-backed helper makes the existing behavior clearer; and
  - do not broaden this into slice-expectation cleanup, report-assertion redesign, or feature/parity work.
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

    assert [manifest.manifest_id for manifest in scorecard_case.manifests] == [
        "module-boundary",
        "collection-replacement-boundary",
        "literal-flag-boundary",
    ]
    assert [manifest.manifest_id for manifest in combined_case.manifests] == [
        "compile-matrix",
        "module-boundary",
        "pattern-boundary",
        "collection-replacement-boundary",
        "literal-flag-boundary",
        "regression-matrix",
    ]
    assert combined_case.target_manifest.manifest_id == "literal-flag-boundary"
    print("ok")
    PY
    ```
  - `rg -n "manifests = load_manifests\\(manifest_paths\\)|manifests = load_manifests\\(list\\(manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not alter benchmark frontier data, workload ids, manifest ordering, built-native behavior, or report contents.
- Prefer selecting `BenchmarkManifest` objects out of the cached source-tree inventory over introducing another path-to-manifest cache layer or reloading a subset with `load_manifests(...)`.
- Do not broaden into source-tree combined slice expectation cleanup, report assertion changes, or the feature work reserved as `RBR-0530`.

## Notes
- `RBR-0530` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0531` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The duplicate surface is concrete and still live:
  - `rg -n "load_manifests\\(manifest_paths\\)|load_manifests\\(list\\(manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py` currently returns the two repeated subset-load call sites in `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)`;
  - `_source_tree_manifest_records()` already caches one combined source-tree inventory built from `compile_smoke.py` plus the published full-suite selector, so those per-case reloads are avoidable; and
  - `source_tree_scorecard_case(...)` currently resolves manifest ids through `manifest_path_for_id(...)` before reloading them, while `source_tree_combined_case(...)` currently reloads the path list returned by `selected_manifest_paths_for_target_manifest(...)`.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`41 passed, 1370 subtests passed in 22.52s`).
  - The inline manifest-order probe above currently prints `ok`.
- 2026-03-17: Routed `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` through cache-backed `BenchmarkManifest` selection helpers built on `_source_tree_manifest_records()`, kept `selected_manifest_paths_for_target_manifest(...)` as a thin path wrapper over the same cached manifest selection, added an identity-based contract that proves the scorecard and combined builders share manifest objects while preserving the expected manifest order for the `post-parser-workflows` and `literal-flag-boundary` cases, and verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline manifest-order probe from this task (`ok`), and `rg -n "manifests = load_manifests\\(manifest_paths\\)|manifests = load_manifests\\(list\\(manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py` (no matches).
