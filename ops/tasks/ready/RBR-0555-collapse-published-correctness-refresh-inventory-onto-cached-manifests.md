# RBR-0555: Collapse published correctness refresh inventory onto cached manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Make `scripts/rebar_ops.py` consume the harness-owned cached published correctness manifest inventory when it decides whether the tracked correctness scorecard needs refresh, instead of rebuilding the same manifest-id list through its own wrapper over `DEFAULT_FIXTURE_PATHS`.

## Deliverables
- `scripts/rebar_ops.py`
- `tests/python/test_readme_reporting.py`

## Acceptance Criteria
- `scripts/rebar_ops.py` deletes the remaining supervisor-local published-correctness inventory wrapper:
  - `def expected_correctness_manifest_ids(...)` is removed; and
  - no `load_fixture_manifests(...)` call remains in that file.
- `published_correctness_report_needs_refresh(...)` derives the expected published manifest ids and count directly from `correctness_harness.published_fixture_manifests()`:
  - do not rebuild `DEFAULT_FIXTURE_PATHS` into a second inventory tuple first;
  - keep the manifest-order comparison identical to the current published scorecard contract; and
  - keep the existing refresh behavior for missing, malformed, narrowed, or legacy-sidecar scorecards.
- `tests/python/test_readme_reporting.py` stops depending on the deleted `rebar_ops.expected_correctness_manifest_ids(...)` wrapper:
  - the two refresh tests still compare the repaired scorecard against the harness-owned published manifest inventory; and
  - do not add a second test-local manifest-id helper that just replaces the deleted script wrapper.
- Preserve current behavior exactly:
  - `refresh_published_correctness_scorecard()` still deletes the retired legacy JSON sidecar when present;
  - a narrowed tracked correctness report still gets regenerated to the full published manifest inventory;
  - the repaired scorecard's `fixtures.manifest_count` and `fixtures.manifest_ids` remain aligned with the published correctness selector order; and
  - do not change correctness fixtures, scorecard payload shapes, benchmark logic, README text, or tracked state files.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.harness_cli_test_support import load_rebar_ops_module

    rebar_ops = load_rebar_ops_module()
    harness = rebar_ops.load_correctness_harness_module()
    payload = harness.SCORECARD_REPORT.load(harness.SCORECARD_REPORT.published_path)
    expected_manifest_ids = [manifest.manifest_id for manifest in harness.published_fixture_manifests()]

    assert payload["fixtures"]["manifest_count"] == len(expected_manifest_ids)
    assert payload["fixtures"]["manifest_ids"] == expected_manifest_ids
    assert rebar_ops.published_correctness_report_needs_refresh(harness) is False
    print("ok")
    PY
    ```
  - `rg -n "def expected_correctness_manifest_ids\\(|load_fixture_manifests\\(|expected_correctness_manifest_ids\\(" scripts/rebar_ops.py tests/python/test_readme_reporting.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change correctness fixture contents, benchmark manifests, Rust code, `python/rebar/`, README/current-status/backlog prose, or published scorecard data.
- Prefer deleting the supervisor-local wrapper over adding another helper layer in `scripts/rebar_ops.py` or `tests/python/test_readme_reporting.py`.
- Do not broaden this into benchmark-report refresh policy or other reporting-path refactors in the same run.

## Notes
- `RBR-0554` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned grouped-alternation bytes follow-on, so `RBR-0555` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short --branch` shows a clean `main...origin/main` checkout.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate refresh-inventory surface is concrete in the current checkout:
  - `rg -n "def expected_correctness_manifest_ids\\(|load_fixture_manifests\\(|expected_correctness_manifest_ids\\(" scripts/rebar_ops.py tests/python/test_readme_reporting.py` currently returns five matches: the script-local wrapper definition, its direct `load_fixture_manifests(...)` call, the refresh check's call site, and two test call sites in `tests/python/test_readme_reporting.py`; and
  - `python/rebar_harness/correctness.py` already owns the cached typed published inventory through `published_fixture_manifests()`, so the supervisor-owned wrapper is now redundant.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py` passes (`7 passed in 1.63s`).
  - The inline probe above prints `ok` in the current checkout.
