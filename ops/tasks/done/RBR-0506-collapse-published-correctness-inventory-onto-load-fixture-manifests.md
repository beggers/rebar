# RBR-0506: Collapse published correctness inventory onto `load_fixture_manifests(...)`

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining repeated published-correctness inventory walks that still loop `DEFAULT_FIXTURE_PATHS` and call `load_fixture_manifest(...)` one file at a time. The intended end state is one obvious typed published-fixture load path, with expectation and anchor helpers deriving from `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` instead of reimplementing the same ordered manifest walk.

## Deliverables
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_correctness_scorecard_registry_contract.py`
- `tests/benchmarks/correctness_anchor_support.py`

## Acceptance Criteria
- `tests/conformance/correctness_expectations.py` collapses its cached published-fixture inventory onto the typed bulk loader:
  - `_fixture_inventory()` (or the local helper that replaces it) loads the published selector through `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)`, not by looping `DEFAULT_FIXTURE_PATHS` and calling `load_fixture_manifest(path)` repeatedly.
  - The helper may keep returning `(path, manifest)` tuples if that is still the clearest shape, but those paths must come from `manifest.path` on the already-loaded `FixtureManifest` records.
  - `correctness_scorecard_target_manifest_ids(...)`, `_expected_target_manifest_ids(...)`, and `_build_scorecard_expectation(...)` preserve the current manifest ordering, representative-case selection, and drift checks for the same published fixture selector.
- `tests/conformance/test_correctness_scorecard_registry_contract.py` stops rebuilding the same inventory with per-path loads:
  - its local fixture inventory helper (or equivalent inline setup) derives path/manifest-id data from `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` or from the typed cached inventory already built in `tests/conformance/correctness_expectations.py`;
  - the registry-contract assertions still prove suite target-manifest ordering follows `DEFAULT_FIXTURE_PATHS`; and
  - the test keeps using real `FixtureManifest.manifest_id` values rather than hard-coded manifest-id lists.
- `tests/benchmarks/correctness_anchor_support.py` stops loading the published correctness suite twice through repeated per-path walks:
  - add one cached published-fixture inventory surface, built from `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)`, and drive both `published_case_ids_by_signature(...)` and `published_cases_by_id()` from that shared typed inventory;
  - keep duplicate published case-id detection intact in `published_cases_by_id()`; and
  - preserve the current anchor mapping behavior for `anchored_workload_case_ids(...)` and `unanchored_workload_ids(...)`.
- Keep current behavior unchanged for the same fixture and workload selections:
  - published correctness manifest order stays identical to `DEFAULT_FIXTURE_PATHS`;
  - `correctness_scorecard_target_manifest_ids("combined")` still starts with the first published manifest id;
  - `published_case_ids_by_signature(...)` still returns the same sorted case-id tuples per signature; and
  - `published_cases_by_id()` still exposes the same keyed case inventory.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`
  - `rg -n 'for (path|fixture_path) in DEFAULT_FIXTURE_PATHS|load_fixture_manifest\\((path|fixture_path)\\)' tests/conformance/correctness_expectations.py tests/conformance/test_correctness_scorecard_registry_contract.py tests/benchmarks/correctness_anchor_support.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifests
    from tests.benchmarks.correctness_anchor_support import published_cases_by_id
    from tests.conformance.correctness_expectations import correctness_scorecard_target_manifest_ids

    manifests = load_fixture_manifests(DEFAULT_FIXTURE_PATHS)
    assert tuple(manifest.path for manifest in manifests) == DEFAULT_FIXTURE_PATHS
    assert correctness_scorecard_target_manifest_ids("combined")[0] == manifests[0].manifest_id
    assert "str-literal-success" in published_cases_by_id()
    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup structural only. Do not change files under `tests/conformance/fixtures/`, do not change `python/rebar_harness/correctness.py`, do not change published scorecards, and do not touch README or tracked state files.
- Prefer the existing typed bulk loader over inventing a new fixture-registry module, filesystem `glob()` discovery path, or a second cached inventory abstraction that shadows `DEFAULT_FIXTURE_PATHS`.
- Do not broaden this task into benchmark manifest cleanup, fixture-selector redesign, or feature-frontier work already reserved as `RBR-0505`.

## Notes
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are all empty in the live filesystem.
  - `git status --short --branch` shows a clean `main` checkout that is only ahead of `origin/main`.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining repeated published-correctness inventory walk is concrete and localized:
  - `rg -n 'for (path|fixture_path) in DEFAULT_FIXTURE_PATHS|load_fixture_manifest\\((path|fixture_path)\\)' tests/conformance/correctness_expectations.py tests/conformance/test_correctness_scorecard_registry_contract.py tests/benchmarks/correctness_anchor_support.py` currently returns 8 matches across exactly these three files.
- 2026-03-17 architecture probes from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_combined_correctness_scorecards.py` passes (`7 passed, 1215 subtests passed in 21.47s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py` passes (`20 passed, 6 subtests passed in 0.15s`).
  - The inline typed-inventory probe above prints `ok`.

## Completion Notes
- 2026-03-17: Collapsed the cached published-correctness inventory in `tests/conformance/correctness_expectations.py` onto `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)`, keeping the existing `(path, manifest)` shape by taking each path from `manifest.path` on the already-loaded typed records.
- Reworked `tests/conformance/test_correctness_scorecard_registry_contract.py` to derive its path and manifest-id view from the typed cached inventory in `tests/conformance/correctness_expectations.py` instead of rebuilding the same ordered inventory with per-path manifest loads.
- Added one cached typed published-fixture inventory in `tests/benchmarks/correctness_anchor_support.py` and reused it for both `published_case_ids_by_signature(...)` and `published_cases_by_id()`, preserving duplicate case-id detection and existing anchor mapping behavior.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`7 passed, 1215 subtests passed in 25.47s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py` (`20 passed, 6 subtests passed in 0.08s`).
  - `rg -n 'for (path|fixture_path) in DEFAULT_FIXTURE_PATHS|load_fixture_manifest\\((path|fixture_path)\\)' tests/conformance/correctness_expectations.py tests/conformance/test_correctness_scorecard_registry_contract.py tests/benchmarks/correctness_anchor_support.py` returned no matches.
  - The task's inline typed-inventory probe prints `ok`.
