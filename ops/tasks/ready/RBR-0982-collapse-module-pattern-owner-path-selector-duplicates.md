# RBR-0982: Collapse module/pattern owner-path selector duplicates

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the duplicated module-vs-pattern owner-path selector pairings from `tests/python/test_module_workflow_parity_suite.py` so the module keyword, pattern keyword, pattern keyword-error, and pattern wrong-text-model publication slices all flow through one file-local generic helper pair instead of keeping two near-identical helper stacks.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines the duplicated module-specific and pattern-specific owner-path selector helpers:
  - `_published_module_keyword_owner_path_fixture_cases(...)`
  - `_selected_module_keyword_owner_path_direct_cases(...)`
  - `_published_pattern_owner_path_fixture_cases(...)`
  - `_selected_pattern_owner_path_direct_cases(...)`
- Replace that duplicated selector stack with one explicit but smaller file-local shared helper surface that is parameterized by owner-path rows and fixture-case collections:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()` derives both the `"module-keyword-helper"` and `"module-keyword-error"` buckets from the shared helper surface instead of the module-specific helper pair;
  - `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()` derives `published_fixture_cases` and `selected_direct_cases` from the shared helper surface with `MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`;
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()` derives both lists from the same shared helper surface with `MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS`;
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()` derives both lists from the same shared helper surface with `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`;
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()` derives both lists from the same shared helper surface with `_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS`; and
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()` derives both lists from the same shared helper surface with `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS`.
- Preserve the current live publication contracts exactly while removing the duplicate helper stacks:
  - the module keyword success slice still resolves to `14` published fixture rows and `14` selected direct rows;
  - the module keyword success text-model split still stays `Counter({"str": 6, "bytes": 8})`;
  - the module keyword success helper split still stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - the module keyword success fixture order still matches `_owner_path_fixture_case_ids(MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the module keyword success selected direct-case order still matches `tuple(row.direct_case.case_id for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the module keyword error slice still resolves to `13` published fixture rows and `13` selected direct rows;
  - the module keyword error text-model split still stays `Counter({"str": 8, "bytes": 5})`;
  - the module keyword error helper split still stays `Counter({"search": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - the module keyword error fixture order still matches `_owner_path_fixture_case_ids(MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS)`;
  - the module keyword error selected direct-case order still matches `tuple(row.direct_case.case_id for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS)`;
  - the pattern keyword success slice still resolves to `27` published fixture rows and `27` selected direct rows;
  - the pattern keyword success text-model split still stays `Counter({"str": 15, "bytes": 12})`;
  - the pattern keyword success helper split still stays `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`;
  - the pattern keyword success fixture order still matches `_owner_path_fixture_case_ids(PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the pattern keyword success selected direct-case order still matches `tuple(row.direct_case.case_id for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the pattern keyword error slice still resolves to `10` published fixture rows and `10` selected direct rows;
  - the pattern keyword error text-model split still stays `Counter({"str": 5, "bytes": 5})`;
  - the pattern keyword error helper split still stays `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - the pattern keyword error fixture order still matches `_owner_path_fixture_case_ids(_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS)`;
  - the pattern keyword error selected direct-case order still matches `tuple(row.direct_case.case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS)`;
  - the pattern wrong-text-model slice still resolves to `6` published fixture rows and `6` selected direct rows;
  - the pattern wrong-text-model text-model split still stays `Counter({"str": 4, "bytes": 2})`;
  - the pattern wrong-text-model helper split still stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`;
  - the pattern wrong-text-model fixture order still matches `_owner_path_fixture_case_ids(_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS)`; and
  - the pattern wrong-text-model selected direct-case order still matches `tuple(row.direct_case.case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS)`.
- Keep the cleanup structural and file-local:
  - keep `_owner_path_fixture_case_ids(...)` and the existing owner-path row dataclasses as the canonical file-local surfaces unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into `_published_compiled_pattern_module_helper_fixture_cases()`, positional-indexlike selector helpers, manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.
- The structural simplification is visible in the file:
  - `rg -n '^def _published_module_keyword_owner_path_fixture_cases\\(|^def _selected_module_keyword_owner_path_direct_cases\\(|^def _published_pattern_owner_path_fixture_cases\\(|^def _selected_pattern_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_CALL_CASES,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    PATTERN_CASES,
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
    _owner_path_fixture_case_ids,
)

module_cases_by_id = {
    case.case_id: case
    for case in MODULE_CALL_CASES
    if not case.use_compiled_pattern
}
pattern_cases_by_id = {case.case_id: case for case in PATTERN_CASES}

checks = (
    (
        "module-keyword-success",
        MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        module_cases_by_id,
        Counter({"str": 6, "bytes": 8}),
        Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4}),
    ),
    (
        "module-keyword-error",
        MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
        module_cases_by_id,
        Counter({"str": 8, "bytes": 5}),
        Counter({"search": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4}),
    ),
    (
        "pattern-keyword-success",
        PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        pattern_cases_by_id,
        Counter({"str": 15, "bytes": 12}),
        Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4}),
    ),
    (
        "pattern-keyword-error",
        _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
        pattern_cases_by_id,
        Counter({"str": 5, "bytes": 5}),
        Counter({"split": 2, "sub": 4, "subn": 4}),
    ),
    (
        "pattern-wrong-text-model",
        _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
        pattern_cases_by_id,
        Counter({"str": 4, "bytes": 2}),
        Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1}),
    ),
)

for label, rows, cases_by_id, expected_text_models, expected_helpers in checks:
    published = tuple(cases_by_id[row.fixture_case_id] for row in rows)
    assert tuple(case.case_id for case in published) == _owner_path_fixture_case_ids(rows)
    assert tuple(row.direct_case.case_id for row in rows)
    assert Counter(case.text_model for case in published) == expected_text_models, label
    assert Counter(case.helper for case in published) == expected_helpers, label

print("ok")
PY`
- `bash -lc "! rg -n '^def _published_module_keyword_owner_path_fixture_cases\\(|^def _selected_module_keyword_owner_path_direct_cases\\(|^def _published_pattern_owner_path_fixture_cases\\(|^def _selected_pattern_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting duplicated selector glue over introducing another abstraction layer.
- Do not edit manifests, benchmark workloads, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0982` is the next available task id in the current checkout:
  - `rg -n 'RBR-0982|RBR-0983|RBR-0984|RBR-0985|RBR-0986' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 15` currently ends at `RBR-0981-publish-pattern-finditer-bounded-str-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'` currently passes (`6 passed, 1441 deselected`);
  - the owner-path row probe in Verification currently passes (`ok`), confirming the five live owner-path publication slices already preserve their current fixture ordering and helper/text-model splits through the canonical row tables; and
  - `rg -n '^def _published_module_keyword_owner_path_fixture_cases\\(|^def _selected_module_keyword_owner_path_direct_cases\\(|^def _published_pattern_owner_path_fixture_cases\\(|^def _selected_pattern_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the duplicated helper stack at lines `2408`, `2419`, `2809`, and `2819`, so the structural no-match check will fail until this cleanup lands.
