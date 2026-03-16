# RBR-0446: Retire the last direct parity fixture-bundle loads

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the last two Python parity/helper tests that still call `load_fixture_bundle(...)` directly, so ordinary parity coverage consistently uses the shared selected-case bundle-spec path and the low-level loader remains exercised only by its dedicated contract tests.

## Deliverables
- `tests/python/test_literal_collection_helpers.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_literal_collection_helpers.py` no longer calls `load_fixture_bundle(...)` directly for `COLLECTION_FIXTURE_BUNDLE`.
- `tests/python/test_literal_collection_helpers.py` switches that one published fixture anchor to the existing shared selected-case helper path by using `SelectedCaseBundleSpec` plus `load_selected_case_fixture_bundles(...)`, while keeping the current selected case ids, expected manifest id, expected pattern set, expected `(operation, helper)` counter, and expected text-model behavior explicit in the test file.
- `tests/python/test_callable_replacement_parity_suite.py` no longer calls `load_fixture_bundle(...)` directly for `COLLECTION_REPLACEMENT_BUNDLE`.
- `tests/python/test_callable_replacement_parity_suite.py` switches that one literal callable anchor to the existing shared selected-case helper path by using `SelectedCaseBundleSpec` plus `load_selected_case_fixture_bundles(...)`, while keeping the current single selected case id, manifest id, expected pattern set, expected `(operation, helper)` counter, and expected text-model behavior explicit in the test file.
- The refactor stays structural only:
  - no fixture membership, case ordering, helper assertions, callable replacement semantics, or parity expectations broaden or shrink; and
  - no changes are made to `tests/conformance/fixtures/*.py`, `python/rebar/`, `python/rebar_harness/`, Rust code, benchmark workloads, published reports, README text, or tracked state files beyond this task file.
- `tests/python/test_fixture_parity_support_contract.py` remains the place that covers direct low-level `load_fixture_bundle(...)` behavior; do not broaden this cleanup into rewriting those helper-contract tests unless a tiny mechanical import adjustment is required.
- After the cleanup:
  - `rg -n 'load_fixture_bundle\\(' tests/python/test_literal_collection_helpers.py tests/python/test_callable_replacement_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_literal_collection_helpers.py tests/python/test_callable_replacement_parity_suite.py`.

## Constraints
- Prefer reusing the existing `SelectedCaseBundleSpec` and `load_selected_case_fixture_bundles(...)` surface from `tests/python/fixture_parity_support.py` over adding another helper type, registry, or support module.
- Keep the selected-case expectations readable in the test files. This cleanup should delete the last direct production-test loader calls, not hide the current fixture anchors behind a generic table that is harder to audit.

## Notes
- `RBR-0445` is already reserved in tracked backlog/current-status state for the next feature-owned benchmark task, so this architecture cleanup starts at `RBR-0446`.
- The runtime dashboard is current and clean (`Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- Outside `tests/python/test_fixture_parity_support_contract.py`, the only remaining direct `load_fixture_bundle(...)` call sites under `tests/python/` are:
  - `tests/python/test_literal_collection_helpers.py`
  - `tests/python/test_callable_replacement_parity_suite.py`
