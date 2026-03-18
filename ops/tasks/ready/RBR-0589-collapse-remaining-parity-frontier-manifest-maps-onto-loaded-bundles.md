# RBR-0589: Collapse remaining parity-frontier manifest maps onto loaded bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete the remaining suite-local manifest-id lookup tables that restate already-loaded parity frontier case ids, so the frontier assertions derive selected rows from each `FixtureBundle` instead of maintaining parallel manifest registries.

## Deliverables
- `tests/python/test_public_surface_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_public_surface_parity_suite.py` removes the local `SELECTED_CASE_IDS_BY_MANIFEST` table and rewrites `test_public_surface_parity_suite_tracks_published_case_frontier()` so it derives `selected_case_ids` directly from `bundle.cases` in the existing bundle order.
- `tests/python/test_quantified_alternation_parity_suite.py` removes the local `SELECTED_CASE_IDS_BY_MANIFEST` table and rewrites `test_quantified_alternation_parity_suite_tracks_published_case_frontier()` so it derives `selected_case_ids` directly from `bundle.cases` in the existing bundle order.
- `tests/python/test_grouped_capture_parity_suite.py` removes both local manifest-id tables:
  - `GROUPED_CAPTURE_TRACKED_CASE_IDS_BY_MANIFEST`
  - `GROUPED_CAPTURE_UNCOVERED_CASE_IDS_BY_MANIFEST`
- The grouped-capture frontier assertion stays exact after the cleanup:
  - `test_grouped_capture_parity_suite_tracks_published_case_frontier()` derives `selected_case_ids` from `bundle.cases` for every manifest except the existing `grouped-match-workflows` special case;
  - the same test keeps `GROUPED_MATCH_TRACKED_CASE_IDS` as the only widened tracked frontier beyond bundle-local rows; and
  - the same test keeps `GROUPED_MATCH_UNCOVERED_CASE_IDS` as the only non-empty uncovered-case allowance, with every other grouped-capture bundle continuing to pass `()`.
- Preserve current behavior exactly:
  - keep the same selected case ids, uncovered case ids, bundle ordering, direct-test bucket contents, grouped-match special-case coverage, bytes follow-on routing, and fixture contract assertions;
  - do not change fixture contents, helper counts, pattern sets, backend behavior, benchmark coverage, or published reports.
- Keep the cleanup structural only:
  - do not edit `tests/python/fixture_parity_support.py`;
  - do not add a new helper, cache, manifest-id dictionary, or suite-local registry layer; and
  - do not touch the active `RBR-0588` benchmark files under `benchmarks/workloads/`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py`
  - ```bash
    python3 - <<'PY'
    from pathlib import Path

    checks = {
        'tests/python/test_public_surface_parity_suite.py': (
            'SELECTED_CASE_IDS_BY_MANIFEST = {',
        ),
        'tests/python/test_quantified_alternation_parity_suite.py': (
            'SELECTED_CASE_IDS_BY_MANIFEST = {',
        ),
        'tests/python/test_grouped_capture_parity_suite.py': (
            'GROUPED_CAPTURE_TRACKED_CASE_IDS_BY_MANIFEST = {',
            'GROUPED_CAPTURE_UNCOVERED_CASE_IDS_BY_MANIFEST = {',
        ),
    }

    failures = []
    for path_str, needles in checks.items():
        text = Path(path_str).read_text()
        for needle in needles:
            if needle in text:
                failures.append(f'{path_str}:still-local:{needle}')

    if failures:
        raise SystemExit('\n'.join(failures))

    print('ok')
    PY
    ```

## Constraints
- Prefer direct `bundle.cases` iteration inside the three frontier tests over another helper or table. This task should delete duplicate representation, not move it.
- Leave `PUBLIC_SURFACE_SELECTED_CASE_IDS`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `GROUPED_MATCH_TRACKED_CASE_IDS`, `GROUPED_MATCH_UNCOVERED_CASE_IDS`, and the direct-test bucket inventories readable in the suite files.
- Do not broaden this run into fixture-support contract edits, bundle-loading changes, benchmark support refactors, or feature work.

## Notes
- `RBR-0588` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active quantified-alternation backtracking-heavy bytes benchmark catch-up, so `RBR-0589` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `677c8b6e89bd14525253eee436f3074f6ff69998` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and aligned in tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The remaining manifest-map drift is concrete in the current checkout:
  - `tests/python/test_public_surface_parity_suite.py` still defines `SELECTED_CASE_IDS_BY_MANIFEST` at line `160`, even though every `selected_case_ids` entry matches the bundle-local case order already loaded into `FIXTURE_BUNDLES`;
  - `tests/python/test_quantified_alternation_parity_suite.py` still defines `SELECTED_CASE_IDS_BY_MANIFEST` at line `568`, and a direct `PYTHONPATH=python ./.venv/bin/python` probe confirms every one of its manifest entries equals `tuple(case.case_id for case in bundle.cases)`;
  - `tests/python/test_grouped_capture_parity_suite.py` still defines `GROUPED_CAPTURE_TRACKED_CASE_IDS_BY_MANIFEST` at line `113` and `GROUPED_CAPTURE_UNCOVERED_CASE_IDS_BY_MANIFEST` at line `123`; and
  - a direct `PYTHONPATH=python ./.venv/bin/python` probe confirms `grouped-match-workflows` is the only grouped-capture manifest where the tracked frontier is wider than `bundle.cases` (`2` bundle rows versus `4` tracked rows), so the full manifest-id maps can shrink to one explicit grouped-match exception without changing coverage.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py` passes (`1158 passed in 0.83s`);
  - the Python probe above currently fails exactly on this cleanup with:
    - `tests/python/test_public_surface_parity_suite.py:still-local:SELECTED_CASE_IDS_BY_MANIFEST = {`
    - `tests/python/test_quantified_alternation_parity_suite.py:still-local:SELECTED_CASE_IDS_BY_MANIFEST = {`
    - `tests/python/test_grouped_capture_parity_suite.py:still-local:GROUPED_CAPTURE_TRACKED_CASE_IDS_BY_MANIFEST = {`
    - `tests/python/test_grouped_capture_parity_suite.py:still-local:GROUPED_CAPTURE_UNCOVERED_CASE_IDS_BY_MANIFEST = {`
