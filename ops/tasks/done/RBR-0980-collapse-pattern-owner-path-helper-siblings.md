# RBR-0980: Collapse pattern owner-path helper siblings

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining split pattern owner-path selector plumbing from `tests/python/test_module_workflow_parity_suite.py` so the pattern-keyword success slice and the pattern type-error publication slices share one file-local row-driven helper path instead of maintaining separate success-specific and type-error-specific selector helpers.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer keeps the current split helper stack for pattern owner-path publication resolution:
  - `_published_pattern_keyword_fixture_cases()`
  - `_pattern_type_error_owner_path_direct_case_ids(...)`
  - `_published_pattern_type_error_owner_path_fixture_cases(...)`
  - `_selected_pattern_type_error_owner_path_direct_cases(...)`
- Replace that split stack with one explicit but smaller file-local shared helper surface that is parameterized by owner-path rows and reused by all three pattern publication slices:
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()` derives both `published_fixture_cases` and `selected_direct_cases` from the shared owner-path helpers with `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`;
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()` derives both lists from the same shared owner-path helpers with `_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS`; and
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()` derives both lists from the same shared owner-path helpers with `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS`.
- Preserve the current live pattern publication contracts exactly:
  - the pattern-keyword success slice still resolves to `27` published fixture rows and `27` selected direct rows;
  - the success text-model split still stays `Counter({"str": 15, "bytes": 12})`;
  - the success helper split still stays `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`;
  - the success fixture order still matches `_owner_path_fixture_case_ids(PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the success selected direct-case order still matches `tuple(row.direct_case.case_id for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the pattern keyword-error slice still resolves to `10` published fixture rows and `10` selected direct rows;
  - the keyword-error helper split still stays `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - the keyword-error fixture order still matches `_owner_path_fixture_case_ids(_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS)`;
  - the keyword-error selected direct-case order still matches `tuple(row.direct_case.case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS)`;
  - the pattern wrong-text-model slice still resolves to `6` published fixture rows and `6` selected direct rows;
  - the wrong-text-model text-model split still stays `Counter({"str": 4, "bytes": 2})`;
  - the wrong-text-model helper split still stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`;
  - the wrong-text-model fixture order still matches `_owner_path_fixture_case_ids(_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS)`; and
  - the wrong-text-model selected direct-case order still matches `tuple(row.direct_case.case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS)`.
- Keep the cleanup structural and file-local:
  - keep `PatternKeywordPublicationOwnerPathRow` and `PatternTypeErrorOwnerPathRow` as the canonical file-local owner-path surfaces unless a strictly smaller file-local successor preserves the same verification surface;
  - do not add a shared helper module, registry, protocol layer, or checked-in data representation; and
  - do not widen this task into module-keyword helpers, compiled-pattern module helpers, positional-indexlike publication, manifests, reports, or tracked state prose.
- The structural simplification is visible in the file:
  - `rg -n '^def _published_pattern_keyword_fixture_cases\\(|^def _pattern_type_error_owner_path_direct_case_ids\\(|^def _published_pattern_type_error_owner_path_fixture_cases\\(|^def _selected_pattern_type_error_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
    _owner_path_fixture_case_ids,
)

assert len(PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS) == 27
assert Counter(row.text_model for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS) == Counter(
    {"str": 15, "bytes": 12}
)
assert tuple(row.fixture_case_id for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS) == (
    _owner_path_fixture_case_ids(PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)
)

assert len(_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS) == 10
assert tuple(row.fixture_case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS) == (
    _owner_path_fixture_case_ids(_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS)
)

assert len(_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS) == 6
assert tuple(row.fixture_case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS) == (
    _owner_path_fixture_case_ids(_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS)
)

print("ok")
PY`
- `bash -lc "! rg -n '^def _published_pattern_keyword_fixture_cases\\(|^def _pattern_type_error_owner_path_direct_case_ids\\(|^def _published_pattern_type_error_owner_path_fixture_cases\\(|^def _selected_pattern_type_error_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting duplicated selector plumbing over introducing another detached abstraction layer.
- Do not edit manifests, benchmark workloads, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0980` is the next available task id in the current checkout:
  - `rg -n 'RBR-0980|RBR-0981|RBR-0982|RBR-0983|RBR-0984' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 15` currently ends at `RBR-0979-catch-up-pattern-findall-bounded-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`4 passed, 1435 deselected`);
  - the owner-path row probe in Verification currently passes (`ok`), confirming the canonical success, keyword-error, and wrong-text-model row tables already preserve the live 27-row, 10-row, and 6-row slices; and
  - `rg -n '^def _published_pattern_keyword_fixture_cases\\(|^def _pattern_type_error_owner_path_direct_case_ids\\(|^def _published_pattern_type_error_owner_path_fixture_cases\\(|^def _selected_pattern_type_error_owner_path_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the split helper stack at lines `2881`, `2890`, `2896`, and `2908`, while the success publication test still carries its own local `direct_cases_by_signature` mirror at line `4876`.

## Completion
- Replaced the split success-only and type-error-only pattern owner-path selector helpers in `tests/python/test_module_workflow_parity_suite.py` with one smaller shared row-based helper pair that selects fixture cases by `fixture_case_id` and direct cases directly from the canonical owner-path rows.
- Switched the success, keyword-error, and wrong-text-model publication tests over to that shared helper surface while preserving the live row counts, text-model/helper splits, and direct/fixture ordering contracts.
- Verified the targeted parity pytest slice passes, the owner-path row probe still reports the expected `27`, `10`, and `6` row tables, and the structural `rg` check returns no matches for the removed helper definitions.
