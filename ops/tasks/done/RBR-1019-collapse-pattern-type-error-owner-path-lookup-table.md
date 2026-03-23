# RBR-1019: Collapse pattern type-error owner-path lookup table

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining `_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID` lookup table from `tests/python/test_module_workflow_parity_suite.py` so the pattern keyword-error and wrong-text-model owner-path rows derive directly from the canonical file-local direct cases instead of routing through a second detached case-id map.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads `_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID`.
- Replace the map-backed construction of `_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS` and `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS` with one smaller file-local route that keeps both tuples as the canonical owner-path surfaces for the same sixteen direct cases:
  - prefer explicit ordered direct-case slices or one equivalent zip over another case-id map, registry, or helper module; and
  - keep `PatternTypeErrorOwnerPathRow` plus the existing owner-path publication helpers as the lower-level contract surface unless a strictly smaller file-local successor preserves the same coverage.
- Preserve the exact keyword-error owner-path order:
  - fixture ids:
    - `workflow-pattern-split-duplicate-maxsplit-keyword-str`
    - `workflow-pattern-split-unexpected-keyword-bytes`
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-after-positional-count-str`
    - `workflow-pattern-sub-count-alias-keyword-str`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-pattern-subn-count-alias-keyword-bytes`
  - matching direct-case ids:
    - `pattern-split-duplicate-maxsplit-keyword-str`
    - `pattern-split-unexpected-keyword-bytes`
    - `pattern-sub-duplicate-count-keyword-str`
    - `pattern-sub-unexpected-keyword-str`
    - `pattern-sub-unexpected-keyword-after-positional-count-str`
    - `pattern-sub-count-alias-keyword-str`
    - `pattern-subn-duplicate-count-keyword-bytes`
    - `pattern-subn-unexpected-keyword-bytes`
    - `pattern-subn-unexpected-keyword-after-positional-count-bytes`
    - `pattern-subn-count-alias-keyword-bytes`
- Preserve the exact wrong-text-model owner-path order:
  - fixture ids:
    - `workflow-pattern-search-str-pattern-on-bytes-string`
    - `workflow-pattern-match-bytes-pattern-on-str-string`
    - `workflow-pattern-fullmatch-str-pattern-on-bytes-string`
    - `workflow-pattern-split-str-pattern-on-bytes-string`
    - `workflow-pattern-sub-str-pattern-on-bytes-string`
    - `workflow-pattern-subn-bytes-pattern-on-str-string`
  - matching direct-case ids:
    - `pattern-search-str-pattern-on-bytes-string`
    - `pattern-match-bytes-pattern-on-str-string`
    - `pattern-fullmatch-str-pattern-on-bytes-string`
    - `pattern-split-str-pattern-on-bytes-string`
    - `pattern-sub-str-pattern-on-bytes-string`
    - `pattern-subn-bytes-pattern-on-str-string`
- Keep the current publication contracts exact while shrinking representation:
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()` stays green with `expected_count=10` and helper counts `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()` stays green with `expected_count=6`, text-model counts `Counter({"str": 4, "bytes": 2})`, and helper counts `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`; and
  - the row tuples above remain the canonical owner-path source for those two tests instead of growing a second local lookup layer.
- Keep the cleanup structural and file-local:
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files; and
  - do not widen this run into pattern keyword success rows, compiled-pattern owner paths, bounded-wildcard publication, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
)

assert tuple(row.fixture_case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS) == (
    "workflow-pattern-split-duplicate-maxsplit-keyword-str",
    "workflow-pattern-split-unexpected-keyword-bytes",
    "workflow-pattern-sub-duplicate-count-keyword-str",
    "workflow-pattern-sub-unexpected-keyword-str",
    "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
    "workflow-pattern-sub-count-alias-keyword-str",
    "workflow-pattern-subn-duplicate-count-keyword-bytes",
    "workflow-pattern-subn-unexpected-keyword-bytes",
    "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
    "workflow-pattern-subn-count-alias-keyword-bytes",
)
assert tuple(row.direct_case.case_id for row in _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS) == (
    "pattern-split-duplicate-maxsplit-keyword-str",
    "pattern-split-unexpected-keyword-bytes",
    "pattern-sub-duplicate-count-keyword-str",
    "pattern-sub-unexpected-keyword-str",
    "pattern-sub-unexpected-keyword-after-positional-count-str",
    "pattern-sub-count-alias-keyword-str",
    "pattern-subn-duplicate-count-keyword-bytes",
    "pattern-subn-unexpected-keyword-bytes",
    "pattern-subn-unexpected-keyword-after-positional-count-bytes",
    "pattern-subn-count-alias-keyword-bytes",
)
assert tuple(row.fixture_case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS) == (
    "workflow-pattern-search-str-pattern-on-bytes-string",
    "workflow-pattern-match-bytes-pattern-on-str-string",
    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
    "workflow-pattern-split-str-pattern-on-bytes-string",
    "workflow-pattern-sub-str-pattern-on-bytes-string",
    "workflow-pattern-subn-bytes-pattern-on-str-string",
)
assert tuple(row.direct_case.case_id for row in _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS) == (
    "pattern-search-str-pattern-on-bytes-string",
    "pattern-match-bytes-pattern-on-str-string",
    "pattern-fullmatch-str-pattern-on-bytes-string",
    "pattern-split-str-pattern-on-bytes-string",
    "pattern-sub-str-pattern-on-bytes-string",
    "pattern-subn-bytes-pattern-on-str-string",
)
print("ok")
PY`
- `bash -lc "! rg -n '^_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the detached id map over adding another lookup layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- `RBR-1019` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1019" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git rev-parse HEAD` matches the dashboard `HEAD` (`196f321727ac559ebfcad3f89f37c3cb2bbc5544`), `git status --short` is empty, and there is no report lag to discount;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID` at line `1509`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'` currently passes (`2 passed, 1449 deselected`);
  - the owner-path order probe in Verification currently passes (`ok`); and
  - `bash -lc "! rg -n '^_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID = ' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on that one remaining detached id map, which is the cleanup being queued here.

## Completion
- 2026-03-23: Replaced `_PATTERN_TYPE_ERROR_DIRECT_CASES_BY_ID` in `tests/python/test_module_workflow_parity_suite.py` with explicit ordered slices of `BOUND_PATTERN_TYPE_ERROR_CASES` zipped directly into `_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS` and `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS`, preserving the published owner-path order without a detached case-id map. Verified with the targeted pytest selector (`2 passed, 1449 deselected`), the owner-path order probe (`ok`), and the no-match `rg` check for the removed lookup table.
