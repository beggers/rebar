# RBR-0871: Promote the selected-fixture bundle helper and collapse the last subset rebuilds

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Promote the selected-row fixture-bundle construction path from the contract test into canonical parity support.
- Delete the remaining hand-built subset bundle rebuilds in the parser-matrix and fixture-backed replacement parity owners so published fixture subsets flow through one validated helper instead of three near-identical implementations.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` exports one canonical selected-row bundle helper for published fixture manifests:
  - promote the logic that currently lives in `_build_selected_fixture_bundle(...)` inside `tests/python/test_fixture_parity_support_contract.py`;
  - keep its current validation behavior for empty selections, duplicate selected ids, missing selected ids, and default `expected_case_ids`; and
  - build the resulting `FixtureBundle` through the existing `build_fixture_bundle(...)` path rather than introducing another spec type, loader layer, or manifest-id registry.
- `tests/python/test_fixture_parity_support_contract.py` stops defining `_build_selected_fixture_bundle(...)` and instead exercises the canonical helper from `tests/python/fixture_parity_support.py`.
- `tests/python/test_parser_matrix_parity_suite.py` no longer rebuilds `PARSER_MATRIX_FIXTURE_BUNDLE` or `CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_BUNDLE` with direct `build_fixture_bundle(...)` calls:
  - keep `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS`, `PARSER_MATRIX_SELECTED_CASE_IDS`, and `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS` unchanged;
  - preserve the current published case order and frontier-coverage assertions; and
  - do not broaden the suite beyond the current parser-only selected rows.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer rebuilds the grouped replacement collection subset with a file-local `case_by_id` plus `build_fixture_bundle(...)` block:
  - derive the ordered `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS` subset through the canonical helper;
  - preserve the current grouped replacement manifest ordering and selected collection rows exactly; and
  - do not broaden the replacement surface or reinterpret bytes-follow-on ownership.
- Keep the cleanup structural only:
  - do not change `tests/conformance/fixtures/`, `python/rebar_harness/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n 'build_fixture_bundle\\(' tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `bash -lc "! rg -n '^def _build_selected_fixture_bundle\\(' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Prefer deleting the duplicated selected-row bundle code over adding another wrapper or another parallel helper family.
- Keep the helper scoped to published fixture bundle selection; do not turn this into a generic fixture-discovery rewrite or a broader parity-suite consolidation.

## Notes
- `RBR-0871` is free in the current checkout:
  - `RBR-0870` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `rg -n "RBR-0871|RBR-0872|RBR-0873" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned no matches.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and already isolated in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1227 passed, 29 skipped in 0.93s`);
  - `bash -lc "! rg -n 'build_fixture_bundle\\(' tests/python/test_parser_matrix_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py"` currently fails exactly on the three remaining suite-local subset rebuilds;
  - `bash -lc "! rg -n '^def _build_selected_fixture_bundle\\(' tests/python/test_fixture_parity_support_contract.py"` currently fails exactly on the contract-only duplicate helper; and
  - `tests/python/test_fixture_parity_support_contract.py`, `tests/python/test_parser_matrix_parity_suite.py`, and `tests/python/test_fixture_backed_replacement_parity_suite.py` all already express the same ordered selected-row bundle contract, so promoting that path into `tests/python/fixture_parity_support.py` deletes duplication without reopening feature behavior.
