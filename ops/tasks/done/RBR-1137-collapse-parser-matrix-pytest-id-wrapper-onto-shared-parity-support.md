## RBR-1137: Collapse parser-matrix pytest id wrapper onto shared parity support

Status: done
Owner: cleanup
Created: 2026-03-24

## Goal
- Remove the remaining suite-local pytest id wrapper from `tests/python/test_parser_matrix_parity_suite.py` by routing its `FixtureCase.case_id` parametrization through the existing shared helper on `tests/python/fixture_parity_support.py`.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` stops defining its suite-local `_fixture_case_id()` wrapper and imports the existing `fixture_case_pytest_id()` helper instead.
- All parser-matrix parametrization ids that currently use `_fixture_case_id()` continue to expose the same `case.case_id` values after the cleanup.
- The cleanup stays local to the parser-matrix parity suite and does not widen into the much larger module-workflow suite or new helper surfaces.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py::test_compile_metadata_matches_cpython tests/python/test_parser_matrix_parity_suite.py::test_compile_only_rows_keep_rebar_search_placeholder tests/python/test_parser_matrix_parity_suite.py::test_compile_cache_identity_and_purge_for_supported_parser_rows tests/python/test_parser_matrix_parity_suite.py::test_compile_diagnostics_match_cpython tests/python/test_parser_matrix_parity_suite.py::test_conditional_assertion_compile_diagnostics_match_cpython tests/python/test_parser_matrix_parity_suite.py::test_rebar_compile_does_not_delegate_to_stdlib_for_selected_parser_rows`
- `bash -lc "! rg -n 'def _fixture_case_id\\(' tests/python/test_parser_matrix_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the parser-matrix parity suite plus this task record.
- Preserve the existing selected parser-matrix frontier, case ordering, and pytest id strings.
- Do not widen this run into the larger `tests/python/test_module_workflow_parity_suite.py` file; that remains a separate cleanup candidate.

## Notes
- `RBR-1137` was unused in this checkout in this run:
  - `rg -n 'RBR-1137|RBR-1138|RBR-1139|RBR-1140' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` only matched historical notes mentioning future-id probes and did not reveal a live task file reserved at `RBR-1137`.
- The cleanup target stayed bounded and local:
  - `tests/python/test_parser_matrix_parity_suite.py` still defined `_fixture_case_id(case: FixtureCase) -> str` even though `tests/python/fixture_parity_support.py` already exports the identical `fixture_case_pytest_id()` helper.
  - The shared helper already has direct support coverage in `tests/python/test_fixture_parity_support_contract.py`, so no new helper surface or contract expansion was needed for this wrapper removal.
