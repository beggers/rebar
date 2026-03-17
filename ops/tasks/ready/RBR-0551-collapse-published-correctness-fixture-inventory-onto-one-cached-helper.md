# RBR-0551: Collapse published correctness fixture inventory onto one cached helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Make `python/rebar_harness/correctness.py` the single owner of the published correctness fixture inventory so the conformance and benchmark expectation helpers stop maintaining their own cached `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` wrappers, and contract tests stop importing a private inventory helper out of `tests/conformance/correctness_expectations.py`.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/correctness_expectations.py`
- `tests/benchmarks/correctness_anchor_support.py`
- `tests/conformance/test_correctness_scorecard_registry_contract.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` grows the smallest shared helper surface needed to own the published fixture inventory:
  - add one cached `published_fixture_manifests()` helper that returns the `FixtureManifest` tuple for `DEFAULT_FIXTURE_PATHS`; and
  - do not add a second selector registry, a parallel path-to-manifest cache, or a new test-only helper module.
- `tests/conformance/correctness_expectations.py` deletes its private published-fixture cache layer:
  - `def _fixture_inventory(...)` is removed;
  - no direct `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` call remains in that file; and
  - prefix fixture-path, manifest-id, and cumulative-layer expectations are derived from `published_fixture_manifests()` instead of a local `(path, manifest)` wrapper cache.
- `tests/benchmarks/correctness_anchor_support.py` deletes its private published-fixture cache layer:
  - `def _published_fixture_inventory(...)` is removed;
  - no direct `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` call remains in that file; and
  - `published_case_ids_by_signature(...)` plus `published_cases_by_id()` still preserve the current published-case order and duplicate-case-id failure behavior while loading through the shared harness helper.
- `tests/conformance/test_correctness_scorecard_registry_contract.py` stops depending on a private helper from another test module:
  - remove the `_fixture_inventory as published_fixture_inventory` import from `tests/conformance/correctness_expectations.py`; and
  - use `published_fixture_manifests()` directly, or a narrower public helper built on top of it, instead of any private inventory alias.
- Add or update focused direct coverage for the new harness-owned helper in `tests/python/test_fixture_parity_support_contract.py` instead of broadening suite-specific parity tests.
- Preserve current behavior exactly:
  - published fixture order remains the current `DEFAULT_FIXTURE_PATHS` order;
  - correctness scorecard target manifest ids, prefix fixture paths, representative-case ordering, and suite/layer expectations remain unchanged for every scorecard suite;
  - benchmark correctness-anchor lookup maps and unanchored workload results remain unchanged for the same signatures; and
  - do not change files under `tests/conformance/fixtures/`, correctness selector ids, benchmark workloads, scorecard payloads, published reports, or `python/rebar/` / Rust behavior.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/python/test_fixture_parity_support_contract.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, published_fixture_manifests

    manifests = published_fixture_manifests()

    assert tuple(manifest.path for manifest in manifests) == DEFAULT_FIXTURE_PATHS
    assert manifests[0].path.name == "parser_matrix.py"
    assert (
        manifests[-1].path.name
        == "conditional_group_exists_callable_replacement_workflows.py"
    )
    print("ok")
    PY
    ```
  - `rg -n "load_fixture_manifests\\(DEFAULT_FIXTURE_PATHS\\)|def _fixture_inventory\\(|def _published_fixture_inventory\\(" tests/conformance/correctness_expectations.py tests/benchmarks/correctness_anchor_support.py`
    The post-change result must be no matches.
  - `rg -n "_fixture_inventory as published_fixture_inventory|published_fixture_inventory\\(" tests/conformance/test_correctness_scorecard_registry_contract.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change fixture contents, parity-suite case selection, benchmark workload rows, published reports, README/current-status/backlog text, or queue another task in the same run.
- Prefer extending `python/rebar_harness/correctness.py` over adding another intermediary helper layer under `tests/`.
- Do not broaden this into selector redesign, scorecard expectation rewrites, or feature/parity work.

## Notes
- `RBR-0550` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned bytes parity follow-on, so `RBR-0551` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The duplicate published-fixture inventory surface is concrete in the current checkout:
  - `rg -n "load_fixture_manifests\\(DEFAULT_FIXTURE_PATHS\\)|def _fixture_inventory\\(|def _published_fixture_inventory\\(" tests/conformance/correctness_expectations.py tests/benchmarks/correctness_anchor_support.py` currently returns four matches: one private correctness cache definition, one private benchmark cache definition, and one direct `load_fixture_manifests(DEFAULT_FIXTURE_PATHS)` call inside each helper;
  - `rg -n "_fixture_inventory as published_fixture_inventory|published_fixture_inventory\\(" tests/conformance/test_correctness_scorecard_registry_contract.py` currently returns three matches: one private-import alias and two call sites in the contract test; and
  - both expectation helper modules are loading the same published fixture inventory through separate local caches even though `DEFAULT_FIXTURE_PATHS` is already the canonical harness-owned selector order.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_scorecard_registry_contract.py tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/python/test_fixture_parity_support_contract.py` passes (`127 passed, 148 subtests passed in 0.66s`).
