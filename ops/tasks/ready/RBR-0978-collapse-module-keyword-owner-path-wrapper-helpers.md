# RBR-0978: Collapse module keyword owner-path wrapper helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining thin module-keyword wrapper helpers from `tests/python/test_module_workflow_parity_suite.py` so the file uses the existing generic owner-path selectors directly instead of carrying one-off functions that only hard-code fixed row tuples into already-generic plumbing.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines the four wrapper helpers that only bind fixed owner-path row tuples:
  - `_published_module_keyword_fixture_cases(...)`
  - `_selected_module_keyword_direct_cases(...)`
  - `_published_module_keyword_error_fixture_cases(...)`
  - `_selected_module_keyword_error_direct_cases(...)`
- Replace those wrappers with direct use of the existing generic helpers at the live call sites:
  - `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases()` derives the `"module-keyword-helper"` and `"module-keyword-error"` frontier buckets from `_published_module_keyword_owner_path_fixture_cases(...)` with the canonical `MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS` and `MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS`;
  - `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()` derives both `published_fixture_cases` and `selected_direct_cases` from `_published_module_keyword_owner_path_fixture_cases(...)` and `_selected_module_keyword_owner_path_direct_cases(...)` with `MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`; and
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()` derives both `published_fixture_cases` and `selected_direct_cases` from `_published_module_keyword_owner_path_fixture_cases(...)` and `_selected_module_keyword_owner_path_direct_cases(...)` with `MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS`.
- Preserve the current live publication contracts exactly while removing the wrappers:
  - the module keyword helper owner-path slice still resolves to `14` published fixture rows and `14` selected direct rows;
  - the module keyword helper text-model split still stays `Counter({"str": 6, "bytes": 8})`;
  - the module keyword helper helper split still stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - the module keyword helper fixture order still matches `_owner_path_fixture_case_ids(MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the module keyword helper selected direct-case order still matches `tuple(row.direct_case.case_id for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the module keyword error owner-path slice still resolves to `13` published fixture rows and `13` selected direct rows;
  - the module keyword error text-model split still stays `Counter({"str": 8, "bytes": 5})`;
  - the module keyword error helper split still stays `Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})`;
  - the module keyword error fixture order still matches `_owner_path_fixture_case_ids(MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS)`; and
  - the module keyword error selected direct-case order still matches `tuple(row.direct_case.case_id for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS)`.
- The cleanup stays structural and file-local:
  - do not add a new helper module, registry, or checked-in data layer; and
  - do not widen this task into pattern-keyword publication, pattern type-error owner paths, benchmark manifests, harness modules, reports, or tracked state prose.
- The structural simplification is visible in the file:
  - `rg -n '^def _published_module_keyword_fixture_cases\\(|^def _selected_module_keyword_direct_cases\\(|^def _published_module_keyword_error_fixture_cases\\(|^def _selected_module_keyword_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _owner_path_fixture_case_ids,
    _published_module_keyword_owner_path_fixture_cases,
    _selected_module_keyword_owner_path_direct_cases,
)

published = _published_module_keyword_owner_path_fixture_cases(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
selected = _selected_module_keyword_owner_path_direct_cases(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    published,
)
assert tuple(case.case_id for case in published) == _owner_path_fixture_case_ids(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in selected) == tuple(
    row.direct_case.case_id for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert len(published) == 14

published_error = _published_module_keyword_owner_path_fixture_cases(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
selected_error = _selected_module_keyword_owner_path_direct_cases(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    published_error,
)
assert tuple(case.case_id for case in published_error) == _owner_path_fixture_case_ids(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in selected_error) == tuple(
    row.direct_case.case_id for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
assert len(published_error) == 13

print("ok")
PY`
- `bash -lc "! rg -n '^def _published_module_keyword_fixture_cases\\(|^def _selected_module_keyword_direct_cases\\(|^def _published_module_keyword_error_fixture_cases\\(|^def _selected_module_keyword_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting wrapper glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0978` is the next available task id in the current checkout:
  - `rg -n 'RBR-0978|RBR-0979|RBR-0980|RBR-0981|RBR-0982' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0977-publish-pattern-findall-bounded-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`5 passed, 1434 deselected`);
  - the generic-owner-path probe in Verification currently passes (`ok`), proving the generic helpers already preserve the live 14-row and 13-row module keyword slices without the thin wrappers; and
  - `rg -n '^def _published_module_keyword_fixture_cases\\(|^def _selected_module_keyword_direct_cases\\(|^def _published_module_keyword_error_fixture_cases\\(|^def _selected_module_keyword_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the dedicated wrapper definitions at lines `2461`, `2467`, `2476`, and `2482`, so the structural no-match check will fail until this cleanup lands.
