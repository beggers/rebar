# RBR-0553: Collapse published benchmark manifest inventory onto one cached helper

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Make `python/rebar_harness/benchmarks.py` the single owner of the published full-suite benchmark manifest inventory so the source-tree benchmark expectation helpers and adjacent benchmark tests stop rebuilding the same selector-plus-load path locally.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
- `tests/benchmarks/test_built_native_benchmark_modes.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` grows the smallest shared helper surface needed to own the published benchmark inventory:
  - add one cached `published_benchmark_manifests()` helper that returns the `BenchmarkManifest` tuple for `PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR`;
  - preserve the current published selector order exactly; and
  - do not add a second selector registry, a parallel path-to-manifest cache, or a new test-only helper module.
- `tests/benchmarks/benchmark_expectations.py` deletes its local published-inventory wrapper layer:
  - `def _compile_smoke_manifest_path(...)` is removed;
  - `def _published_full_suite_manifest_paths(...)` is removed;
  - `def _published_source_tree_manifests(...)` is removed;
  - `_source_tree_manifest_records()` builds its cache from `published_benchmark_manifests()` plus one direct compile-smoke manifest load instead of reloading the entire published full suite through local path wrappers; and
  - `source_tree_combined_target_manifest_ids()` plus `_selected_source_tree_manifests_for_target_manifest(...)` derive published selector order directly from `published_benchmark_manifests()` instead of any private wrapper alias.
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` adds or updates focused coverage for the new harness-owned helper instead of open-coding the published full-suite load path when it only needs typed manifests:
  - no `load_manifests(list(published_manifest_paths))` call remains in that file; and
  - the contract still proves published manifest order plus unique manifest ids and workload ids for the full suite.
- `tests/benchmarks/test_built_native_benchmark_modes.py` stops open-coding the published full-suite manifest load when it only needs inventory totals for the native full-suite report assertion:
  - no `load_manifests(list(published_manifest_paths))` call remains in that file; and
  - the native full-suite known-gap test still derives the same expected manifest/workload totals from `published_benchmark_manifests()`.
- Preserve current behavior exactly:
  - `published_benchmark_manifests()` returns the same ordered manifest set as `select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)`;
  - compile-smoke remains outside the published full-suite helper;
  - source-tree scorecard case ids, combined target manifest ids, regression-manifest append behavior, selected workload ids, known-gap counts, and representative workload ids remain unchanged; and
  - do not change files under `benchmarks/workloads/`, benchmark selector ids, built-native mode semantics, scorecard payloads, or published reports.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_built_native_benchmark_modes.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from rebar_harness.benchmarks import (
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
        published_benchmark_manifests,
        select_benchmark_manifest_paths,
    )

    manifests = published_benchmark_manifests()

    assert published_benchmark_manifests() is manifests
    assert tuple(manifest.path for manifest in manifests) == select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    assert manifests[0].path.name == "compile_matrix.py"
    assert manifests[-1].path.name == "regression_matrix.py"
    print("ok")
    PY
    ```
  - `rg -n "def _compile_smoke_manifest_path\\(|def _published_full_suite_manifest_paths\\(|def _published_source_tree_manifests\\(|load_manifests\\(list\\(published_manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_built_native_benchmark_modes.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change benchmark workloads, correctness fixtures, selector ids, report payloads, published reports, or widen into feature/parity work.
- Prefer extending `python/rebar_harness/benchmarks.py` over adding another intermediary helper layer under `tests/`.
- Do not redesign manifest selectors or built-native runner plumbing in the same run.

## Notes
- `RBR-0552` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned benchmark follow-on, so `RBR-0553` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate benchmark-inventory surface is concrete in the current checkout:
  - `rg -n "def _compile_smoke_manifest_path\\(|def _published_full_suite_manifest_paths\\(|def _published_source_tree_manifests\\(|load_manifests\\(list\\(published_manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_built_native_benchmark_modes.py` currently returns five matches: three private wrapper definitions in `tests/benchmarks/benchmark_expectations.py` plus one direct published-manifest load in each of the two test modules; and
  - `tests/benchmarks/benchmark_expectations.py` currently reloads the entire published full suite through `_source_tree_manifest_records()` even though the harness already owns the selector-to-manifest mapping.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_built_native_benchmark_modes.py` passes (`59 passed, 2 skipped, 1523 subtests passed in 21.96s`).
  - The post-change helper probe in this task currently fails with `ImportError: cannot import name 'published_benchmark_manifests' from 'rebar_harness.benchmarks'`, which is the exact missing helper this cleanup is meant to add.
- Completed 2026-03-17:
  - Added `published_benchmark_manifests()` to `python/rebar_harness/benchmarks.py` as the single cached typed-manifest helper for `PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR`.
  - Removed the local published full-suite wrapper helpers from `tests/benchmarks/benchmark_expectations.py`, leaving its source-tree manifest cache to build from one direct compile-smoke manifest load plus `published_benchmark_manifests()`.
  - Updated `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` and `tests/benchmarks/test_built_native_benchmark_modes.py` to consume `published_benchmark_manifests()` when they need typed manifest inventory totals or ordered manifest records.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_built_native_benchmark_modes.py` (`60 passed, 2 skipped, 1523 subtests passed in 22.06s`).
  - Verified the new helper directly with the task’s `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` snippet (`ok`).
  - Verified the duplicate published-inventory wrapper layer is gone with `rg -n "def _compile_smoke_manifest_path\\(|def _published_full_suite_manifest_paths\\(|def _published_source_tree_manifests\\(|load_manifests\\(list\\(published_manifest_paths\\)\\)" tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_built_native_benchmark_modes.py`, which now returns no matches.
