# RBR-0451: Retire the last direct parser parity fixture-manifest loads

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the last ordinary Python parity suite that still calls `load_fixture_manifest(...)` directly, so parser-focused parity coverage goes through the same shared selected-case bundle path as the rest of the parity surface and low-level manifest loading remains exercised only by helper-support code plus its dedicated contract tests.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` no longer imports or calls `load_fixture_manifest(...)`.
- The suite switches both published fixture anchors, `parser_matrix.py` and `conditional_group_exists_assertion_diagnostics.py`, to the existing `SelectedCaseBundleSpec` plus `load_selected_case_fixture_bundles(...)` path from `tests/python/fixture_parity_support.py`.
- The parser-matrix rewrite preserves the current `EXPECTED_CASE_IDS` order exactly and keeps the same selected published slice behind:
  `TARGET_CASES`, `COMPILE_METADATA_CASES`, `PLACEHOLDER_SEARCH_CASES`, `REPEATED_COMPILE_CACHE_CASES`, `DIAGNOSTIC_CASES`, `NO_STDLIB_DELEGATION_CASES`, `NESTED_SET_WARNING_CASE`, `CHARACTER_CLASS_CASE`, and `PLACEHOLDER_SEARCH_SUBJECTS`.
- The conditional-assertion-diagnostic rewrite preserves the current `EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS` order exactly and the current `EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_PATTERNS` set exactly.
- The existing alignment tests in `tests/python/test_parser_matrix_parity_suite.py` still assert the same manifest paths, manifest ids, selected case ids, and compile-only `(operation, helper)` shape for both fixture anchors.
- If the selected-case bundle rewrite needs new explicit expected pattern sets or `(operation, helper)` counters, keep those expectations file-local in `tests/python/test_parser_matrix_parity_suite.py`; do not add a new selector registry, bundle catalog, or support module for this cleanup.
- Prefer a suite-local refactor only:
  `tests/python/fixture_parity_support.py` and `tests/python/test_fixture_parity_support_contract.py` should remain unchanged unless a tiny helper is genuinely unavoidable.
- If a helper is genuinely unavoidable, keep it limited to ordered case selection from already-loaded bundle data and add focused contract coverage in `tests/python/test_fixture_parity_support_contract.py`.
- The cleanup stays structural only:
  do not change `tests/conformance/fixtures/*.py`, `python/rebar_harness/`, `python/rebar/`, Rust code, benchmark workloads, published reports, README text, or tracked state files beyond this task file.
- After the cleanup:
  `rg -n 'load_fixture_manifest\\(' tests/python/test_parser_matrix_parity_suite.py` returns no matches.
- After the cleanup:
  `rg -n 'load_fixture_manifest\\(' tests/python/*.py` shows matches only in `tests/python/fixture_parity_support.py` and `tests/python/test_fixture_parity_support_contract.py`.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py`.

## Constraints
- Prefer reusing the existing `SelectedCaseBundleSpec` and `load_selected_case_fixture_bundles(...)` surface over adding another abstraction layer.
- Keep the selected case ids and any new expected pattern or counter constants readable in the suite file. This task should delete one remaining low-level manifest bypass, not hide the parser anchors behind a generic registry.

## Notes
- `RBR-0449` and `RBR-0450` are already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned anchored compile milestone, so this architecture cleanup starts at `RBR-0451`.
- The runtime dashboard is current and clean (`Generated: 2026-03-16T05:44:32+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, and `rg --files -g '*.json' | wc -l = 0`.
- `rg -n "load_fixture_manifest\\(|load_fixture_manifests\\(" tests/python -S` currently shows direct manifest loads only in:
  `tests/python/test_parser_matrix_parity_suite.py`, `tests/python/fixture_parity_support.py`, and `tests/python/test_fixture_parity_support_contract.py`.
- That leaves `tests/python/test_parser_matrix_parity_suite.py` as the last ordinary parity-suite bypass around the shared fixture-bundle path.

## Completion
- 2026-03-16: Rewrote `tests/python/test_parser_matrix_parity_suite.py` to load both `parser_matrix.py` and `conditional_group_exists_assertion_diagnostics.py` through file-local `SelectedCaseBundleSpec` entries plus `load_selected_case_fixture_bundles(...)`, preserving the existing selected case ids, case ordering, and suite-local compile/module grouping constants.
- 2026-03-16: Kept the alignment assertions in that suite local by checking each bundle's manifest path, manifest id, explicit ordered case ids, expected pattern set, and compile-only `(operation, helper)` counter through the existing fixture-bundle contract helper.
- 2026-03-16: Verified `rg -n 'load_fixture_manifest\\(' tests/python/test_parser_matrix_parity_suite.py` returned no matches, `rg -n 'load_fixture_manifest\\(' tests/python/*.py` now shows matches only in `tests/python/fixture_parity_support.py` and `tests/python/test_fixture_parity_support_contract.py`, and `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py` passed (`113 passed, 23 skipped in 0.16s`).
