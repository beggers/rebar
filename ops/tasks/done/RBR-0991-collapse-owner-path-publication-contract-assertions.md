# RBR-0991: Collapse owner-path publication contract assertions

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated owner-path publication contract scaffolding from `tests/python/test_module_workflow_parity_suite.py` so the module, pattern, and compiled-pattern owner-path slices assert through one smaller file-local contract helper instead of open-coding the same setup and invariant checks across six tests.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for owner-path publication contracts, or a strictly smaller equivalent, that centralizes the repeated setup currently open-coded in these tests:
  - `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`
- Repoint those six tests through the shared helper surface instead of repeating the same `published_fixture_cases` / `selected_direct_cases` setup and baseline ordering checks inline.
- Preserve the current live publication contracts exactly while removing the repeated assertion scaffolding:
  - module keyword success still resolves to `14` published fixture rows and `14` selected direct rows, with `Counter({"str": 6, "bytes": 8})` and `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - module keyword error still resolves to `13` published fixture rows and `13` selected direct rows, with `Counter({"str": 8, "bytes": 5})` and `Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})`;
  - pattern keyword success still resolves to `27` published fixture rows and `27` selected direct rows, with `Counter({"str": 15, "bytes": 12})` and `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`;
  - pattern keyword error still resolves to `10` published fixture rows and `10` selected direct rows, with `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - pattern wrong-text-model still resolves to `6` published fixture rows and `6` selected direct rows, with `Counter({"str": 4, "bytes": 2})` and `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`;
  - compiled-pattern module-helper success still resolves to `62` published fixture rows and `62` selected direct rows, with `Counter({"str": 33, "bytes": 29})` and `Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10})`.
- Preserve the canonical row-driven ordering contracts:
  - each targeted slice still keeps `tuple(case.case_id for case in published_fixture_cases) == _owner_path_fixture_case_ids(rows)` for its row table;
  - each targeted slice still keeps `tuple(case.case_id for case in selected_direct_cases) == tuple(row.direct_case.case_id for row in rows)`; and
  - compiled-pattern module-helper coverage still keeps helper ordering aligned with `_compiled_pattern_module_helper_direct_case_helper(...)` rather than raw `.helper` access.
- Keep the cleanup structural and file-local:
  - keep `_published_owner_path_fixture_cases(...)`, `_selected_owner_path_direct_cases(...)`, `_owner_path_fixture_case_ids(...)`, and the existing owner-path row tables as the canonical selector surface unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into positional-indexlike helpers, collection helpers, bounded-wildcard helpers, manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'publishes_module_keyword_helpers_from_direct_cases or publishes_module_keyword_error_slice_from_direct_cases or publishes_pattern_keyword_helpers_from_direct_cases or publishes_pattern_keyword_error_slice_from_direct_cases or publishes_pattern_wrong_text_model_slice_from_direct_cases or publishes_compiled_pattern_module_helpers_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    RAW_MODULE_CALL_CASES,
    PATTERN_CASES,
    MODULE_CALL_CASES,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
    _published_owner_path_fixture_cases,
    _selected_owner_path_direct_cases,
    _owner_path_fixture_case_ids,
    _compiled_pattern_module_helper_direct_case_helper,
)

module_keyword_cases = _published_owner_path_fixture_cases(
    RAW_MODULE_CALL_CASES, MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
module_keyword_direct_cases = _selected_owner_path_direct_cases(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in module_keyword_cases) == _owner_path_fixture_case_ids(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in module_keyword_direct_cases) == tuple(
    row.direct_case.case_id for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert Counter(case.text_model for case in module_keyword_cases) == Counter({"str": 6, "bytes": 8})
assert Counter(case.helper for case in module_keyword_cases) == Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})
assert tuple(case.helper for case in module_keyword_cases) == tuple(case.helper for case in module_keyword_direct_cases)

module_keyword_error_cases = _published_owner_path_fixture_cases(
    RAW_MODULE_CALL_CASES, MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
module_keyword_error_direct_cases = _selected_owner_path_direct_cases(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in module_keyword_error_cases) == _owner_path_fixture_case_ids(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in module_keyword_error_direct_cases) == tuple(
    row.direct_case.case_id for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)
assert Counter(case.text_model for case in module_keyword_error_cases) == Counter({"str": 8, "bytes": 5})
assert Counter(case.helper for case in module_keyword_error_cases) == Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})
assert tuple(case.helper for case in module_keyword_error_cases) == tuple(case.helper for case in module_keyword_error_direct_cases)

pattern_keyword_cases = _published_owner_path_fixture_cases(
    PATTERN_CASES, PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
pattern_keyword_direct_cases = _selected_owner_path_direct_cases(
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_keyword_cases) == _owner_path_fixture_case_ids(
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_keyword_direct_cases) == tuple(
    row.direct_case.case_id for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)
assert Counter(case.text_model for case in pattern_keyword_cases) == Counter({"str": 15, "bytes": 12})
assert Counter(case.helper for case in pattern_keyword_cases) == Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})
assert tuple(case.helper for case in pattern_keyword_cases) == tuple(case.helper for case in pattern_keyword_direct_cases)

pattern_keyword_error_cases = _published_owner_path_fixture_cases(
    PATTERN_CASES, _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS
)
pattern_keyword_error_direct_cases = _selected_owner_path_direct_cases(
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_keyword_error_cases) == _owner_path_fixture_case_ids(
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_keyword_error_direct_cases) == tuple(
    row.direct_case.case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS
)
assert Counter(case.helper for case in pattern_keyword_error_cases) == Counter({"split": 2, "sub": 4, "subn": 4})
assert tuple(case.helper for case in pattern_keyword_error_cases) == tuple(case.helper for case in pattern_keyword_error_direct_cases)

pattern_wrong_text_model_cases = _published_owner_path_fixture_cases(
    PATTERN_CASES, _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS
)
pattern_wrong_text_model_direct_cases = _selected_owner_path_direct_cases(
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_wrong_text_model_cases) == _owner_path_fixture_case_ids(
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in pattern_wrong_text_model_direct_cases) == tuple(
    row.direct_case.case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS
)
assert Counter(case.text_model for case in pattern_wrong_text_model_cases) == Counter({"str": 4, "bytes": 2})
assert Counter(case.helper for case in pattern_wrong_text_model_cases) == Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})
assert tuple(case.helper for case in pattern_wrong_text_model_cases) == tuple(case.helper for case in pattern_wrong_text_model_direct_cases)

compiled_pattern_module_cases = _published_owner_path_fixture_cases(
    MODULE_CALL_CASES, COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS
)
compiled_pattern_module_direct_cases = _selected_owner_path_direct_cases(
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in compiled_pattern_module_cases) == _owner_path_fixture_case_ids(
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS
)
assert tuple(case.case_id for case in compiled_pattern_module_direct_cases) == tuple(
    row.direct_case.case_id for row in COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS
)
assert Counter(case.text_model for case in compiled_pattern_module_cases) == Counter({"str": 33, "bytes": 29})
assert Counter(case.helper for case in compiled_pattern_module_cases) == Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10})
assert tuple(case.helper for case in compiled_pattern_module_cases) == tuple(
    _compiled_pattern_module_helper_direct_case_helper(case)
    for case in compiled_pattern_module_direct_cases
)

print('ok')
PY`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting repeated assertion glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0991` is the next available task id in the current checkout:
  - `rg -n 'RBR-0991|RBR-0992|RBR-0993|RBR-0994|RBR-0995' ops/state/backlog.md ops/state/current_status.md` returned no tracked reservation in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0990-collapse-module-pattern-collection-direct-helper-selectors.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `rg -n 'published_fixture_cases = _published_owner_path_fixture_cases\\(|selected_direct_cases = _selected_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds twelve open-coded setup lines across the shared-owner-path frontier tests, including the six slices targeted here;
  - the focused pytest slice in Verification currently passes (`6 passed, 1445 deselected`); and
  - the owner-path contract probe in Verification currently passes (`ok`), confirming that this cleanup can stay structural while preserving the current row-driven ordering and count contracts.

## Completion
- Added one file-local `_assert_owner_path_publication_contract(...)` helper in `tests/python/test_module_workflow_parity_suite.py` to centralize owner-path fixture/direct-case selection, row ordering, optional text-model count checks, and helper-order assertions.
- Repointed the six targeted owner-path publication tests through that helper while keeping each test's fixture-vs-direct-case field assertions local and unchanged in behavior, including the compiled-pattern helper ordering special case.
- Verified with the focused pytest slice (`6 passed, 1445 deselected`) and the explicit owner-path contract probe (`ok`).
