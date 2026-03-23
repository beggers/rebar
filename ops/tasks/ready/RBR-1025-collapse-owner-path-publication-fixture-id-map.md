# RBR-1025: Collapse owner-path publication fixture-id map

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining local `fixture_cases_by_id` lookup map from `_assert_owner_path_publication_contract()` in `tests/python/test_module_workflow_parity_suite.py` so the shared owner-path publication helper selects fixture cases directly from the canonical file-local case tuples instead of rebuilding a detached case-id dictionary for every contract check.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads `fixture_cases_by_id` inside `_assert_owner_path_publication_contract()`.
- Replace the map-backed `published_fixture_cases` selection with one smaller file-local route built from the existing canonical tuple inputs:
  - prefer `_case_with_id(...)`, `_cases_with_ids(...)`, or one strictly smaller equivalent over another case-id map, registry, or helper module; and
  - keep `_assert_owner_path_publication_contract()` as the canonical shared owner-path contract helper unless a strictly smaller file-local successor preserves the same verification surface.
- Preserve the current owner-path publication contracts exactly for the shared helper callers:
  - module keyword publication rows still resolve to `14` fixture/direct-case pairs with text-model counts `Counter({"str": 6, "bytes": 8})` and helper counts `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - pattern keyword publication rows still resolve to `27` fixture/direct-case pairs with text-model counts `Counter({"str": 15, "bytes": 12})` and helper counts `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`;
  - pattern keyword-error rows still resolve to `10` fixture/direct-case pairs with helper counts `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - pattern wrong-text-model rows still resolve to `6` fixture/direct-case pairs with text-model counts `Counter({"str": 4, "bytes": 2})` and helper counts `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`; and
  - compiled-pattern module-helper rows still resolve to `62` fixture/direct-case pairs with text-model counts `Counter({"str": 33, "bytes": 29})` and helper counts `Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10})`, including the existing compiled-pattern-specific `direct_case_helper` path.
- Keep the cleanup structural and local:
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files; and
  - do not widen this run into owner-row tuple reshaping, bounded-wildcard cleanup, positional-indexlike cleanup, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'publishes_module_keyword_helpers_from_direct_cases or publishes_pattern_keyword_helpers_from_direct_cases or publishes_pattern_keyword_error_slice_from_direct_cases or publishes_pattern_wrong_text_model_slice_from_direct_cases or publishes_compiled_pattern_module_helpers_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_WORKFLOW_BUNDLE,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
    _assert_owner_path_publication_contract,
    _compiled_pattern_module_helper_publication_signature,
    _owner_path_fixture_case_ids,
)

fixture_cases = tuple(MODULE_WORKFLOW_BUNDLE.cases)
for rows, expected_count, helper_counts, text_model_counts, direct_case_helper in (
    (
        MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        14,
        Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4}),
        Counter({"str": 6, "bytes": 8}),
        None,
    ),
    (
        PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        27,
        Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4}),
        Counter({"str": 15, "bytes": 12}),
        None,
    ),
    (
        _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
        10,
        Counter({"split": 2, "sub": 4, "subn": 4}),
        None,
        None,
    ),
    (
        _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
        6,
        Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1}),
        Counter({"str": 4, "bytes": 2}),
        None,
    ),
    (
        COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
        62,
        Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10}),
        Counter({"str": 33, "bytes": 29}),
        lambda case: _compiled_pattern_module_helper_publication_signature(case)[0],
    ),
):
    published_fixture_cases, selected_direct_cases = _assert_owner_path_publication_contract(
        fixture_cases,
        rows,
        expected_count=expected_count,
        expected_helper_counts=helper_counts,
        expected_text_model_counts=text_model_counts,
        direct_case_helper=direct_case_helper,
    )
    assert tuple(case.case_id for case in published_fixture_cases) == _owner_path_fixture_case_ids(rows)
    assert tuple(case.case_id for case in selected_direct_cases) == tuple(
        row.direct_case.case_id for row in rows
    )
print("ok")
PY`
- `bash -lc "! rg -n 'fixture_cases_by_id = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the detached fixture-id map over introducing another selector layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- `RBR-1025` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1025" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/loop_state.json` reports `tracked_json_blob_count: 0`;
  - `git status --short` was empty in this run;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `fixture_cases_by_id` inside `_assert_owner_path_publication_contract()` at line `2469`;
  - the pytest selector in Verification currently passes (`5 passed, 1446 deselected`);
  - the inline owner-path contract probe in Verification currently reports `ok`; and
  - the final `! rg ...` check currently fails exactly on the detached map being queued for removal here.
