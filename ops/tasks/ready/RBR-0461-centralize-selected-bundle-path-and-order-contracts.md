# RBR-0461: Centralize selected-bundle path and order contracts

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Extend the shared fixture-bundle contract so selected-case parity suites can assert fixture path and ordered case ids through one support surface instead of repeating the same bundle-alignment checks in individual tests.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- Prefer extending the existing `assert_fixture_bundle_contract(...)` surface in `tests/python/fixture_parity_support.py`, or add only the smallest immediately adjacent helper if a signature change would be awkward. Do not add a new registry, support module, generated table, or suite-specific wrapper layer.
- The shared contract surface can now optionally validate both of these invariants for a loaded `FixtureBundle`:
  - the expected fixture path; and
  - the exact ordered case-id tuple for selected-case bundles.
- `tests/python/test_fixture_parity_support_contract.py` adds focused coverage for the new shared-contract behavior while keeping the existing bundle-order and published-path checks intact:
  - one happy-path assertion that validates a selected-case bundle with both expected path and ordered case ids;
  - one happy-path assertion that validates a whole-manifest bundle with expected path only; and
  - one mismatch assertion proving the new ordered-case contract fails loudly when the caller supplies the wrong case order.
- `tests/python/test_module_workflow_parity_suite.py` routes `test_module_workflow_parity_suite_stays_aligned_with_published_fixture()` through the shared contract surface instead of open-coding the current bundle path, manifest id, ordered case-id, and operation/helper-count checks there.
- `tests/python/test_parser_matrix_parity_suite.py` routes both existing bundle-alignment tests through the shared contract surface instead of open-coding the overlapping bundle path, manifest id, ordered case-id, operation/helper-count, and pattern-set checks that the shared helper already owns:
  - `test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture()`
  - `test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture()`
- Keep the suite-local frontier assertions that are not ordinary bundle-contract invariants untouched, including:
  - `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS`
  - `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS`
  - the verbose `module_workflow_surface.py` workflow cases and compiled-pattern helper cases.
- The cleanup stays structural only:
  - do not change correctness fixture contents, Rust code, `python/rebar/`, `python/rebar_harness/`, benchmark workloads, published reports, README text, or tracked state files beyond this task file; and
  - do not broaden into other parity suites such as `tests/python/test_literal_flag_parity_suite.py`, `tests/python/test_grouped_capture_parity_suite.py`, or `tests/python/test_conditional_group_exists_quantified_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_module_workflow_parity_suite.py tests/python/test_parser_matrix_parity_suite.py`

## Constraints
- Prefer deleting duplicated assertions over creating another assertion layer. The intended end state is one ordinary fixture-bundle contract surface in `tests/python/fixture_parity_support.py`, not a family of near-duplicate bundle checkers.
- Preserve the current selected case ids, manifest ids, case ordering, text-model expectations, and parity coverage exactly. This task should only move repeated contract checks behind shared support.
- Keep the helper readable from the parity suites. Do not hide bundle expectations behind a registry keyed by suite name or fixture name.

## Notes
- `RBR-0460` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned parser-stress parity follow-on, so this architecture cleanup starts at `RBR-0461`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T09:22:20+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, the remaining manual path/order contract checks are concentrated in the parity/support surface that already depends on `assert_fixture_bundle_contract(...)`:
  - `tests/python/test_module_workflow_parity_suite.py:280-285`
  - `tests/python/test_parser_matrix_parity_suite.py:277-284`
  - `tests/python/test_parser_matrix_parity_suite.py:323-334`
  - `tests/python/test_fixture_parity_support_contract.py:619-622`
- Those assertions are all checking data that is already present on `FixtureBundle` or derived from the selected-case bundle spec path, so they are a good bounded follow-on after `RBR-0427`, `RBR-0434`, `RBR-0438`, `RBR-0446`, `RBR-0448`, and `RBR-0451`.
