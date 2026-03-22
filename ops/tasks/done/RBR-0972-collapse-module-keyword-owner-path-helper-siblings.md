# RBR-0972: Collapse module-keyword owner-path helper siblings

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining success-versus-keyword-error owner-path helper duplication in `tests/python/test_module_workflow_parity_suite.py` so the module-keyword publication slice runs through one shared file-local helper path instead of maintaining four near-identical sibling functions.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer keeps four sibling module-keyword owner-path helpers with duplicated row-to-signature resolution logic:
  - `_published_module_keyword_fixture_cases()`
  - `_selected_module_keyword_direct_cases(...)`
  - `_published_module_keyword_error_fixture_cases()`
  - `_selected_module_keyword_error_direct_cases(...)`
- Replace those sibling bodies with one explicit but smaller file-local shared helper surface that is parameterized by the owner-path rows and reused by both the success and keyword-error publication slices:
  - keep the cleanup local to `tests/python/test_module_workflow_parity_suite.py`;
  - prefer one helper for published fixture-case resolution plus one helper for selected direct-case resolution, or an equivalent file-local shape;
  - keep `MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS` and `MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS` as the live owner-path tables unless a strictly smaller file-local successor preserves the same verification surface; and
  - do not add a shared helper module, registry, or checked-in data layer.
- Preserve the current live module-keyword publication contracts exactly:
  - `_published_module_keyword_fixture_cases()` still resolves to `14` published fixture rows;
  - `_published_module_keyword_error_fixture_cases()` still resolves to `13` published fixture rows;
  - the success text-model split stays `Counter({"str": 6, "bytes": 8})`;
  - the keyword-error text-model split stays `Counter({"str": 8, "bytes": 5})`;
  - the success helper split stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - the keyword-error helper split stays `Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})`;
  - the full published success fixture order still matches `_module_keyword_owner_path_fixture_case_ids(MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS)`;
  - the full published keyword-error fixture order still matches `_module_keyword_owner_path_fixture_case_ids(MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS)`; and
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()` stays green without widening this cleanup into pattern-keyword, compiled-pattern, positional-indexlike, or benchmark/report plumbing.
- The structural duplication reduction must be visible in the file:
  - the raw occurrence count of `_module_keyword_direct_signature(row.direct_case)` drops to at most `2`;
  - the raw occurrence count of `for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS` drops to at most `2`; and
  - the raw occurrence count of `for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS` drops to at most `2`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or module_workflow_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _module_keyword_owner_path_fixture_case_ids,
    _published_module_keyword_error_fixture_cases,
    _published_module_keyword_fixture_cases,
)

published = _published_module_keyword_fixture_cases()
errors = _published_module_keyword_error_fixture_cases()

assert len(published) == 14
assert Counter(case.text_model for case in published) == Counter({"str": 6, "bytes": 8})
assert Counter(case.helper for case in published) == Counter(
    {"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4}
)
assert tuple(case.case_id for case in published) == _module_keyword_owner_path_fixture_case_ids(
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
)

assert len(errors) == 13
assert Counter(case.text_model for case in errors) == Counter({"str": 8, "bytes": 5})
assert Counter(case.helper for case in errors) == Counter(
    {"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4}
)
assert tuple(case.case_id for case in errors) == _module_keyword_owner_path_fixture_case_ids(
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS
)

print("ok", len(published), len(errors))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count("_module_keyword_direct_signature(row.direct_case)") <= 2
assert text.count("for row in MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS") <= 2
assert text.count("for row in MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS") <= 2

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path helper plumbing over introducing another detached representation layer.

## Notes
- `RBR-0972` is the next available task id in the current checkout:
  - `rg -n "RBR-0972|RBR-0973|RBR-0974|RBR-0975" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no concrete reserved future task using this id in the current checkout; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0971-catch-up-pattern-bounded-wildcard-sextet.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or module_workflow_direct_test_buckets_cover_selected_frontier'` currently passes (`3 passed, 1430 deselected`);
  - the combined publication-contract probe in Verification currently passes (`ok 14 13`), proving both module-keyword publication slices already resolve to the expected live owner-path surfaces; and
  - the structural probe in Verification now passes because the four module-keyword owner-path sibling helpers have been collapsed behind one file-local published-fixture resolver and one file-local selected-direct-case resolver.

## Completion
- Replaced the four sibling module-keyword owner-path helpers in `tests/python/test_module_workflow_parity_suite.py` with one shared published-fixture resolver and one shared selected-direct-case resolver, both still driven by the existing success and keyword-error owner-path row tables.
- Verified the targeted module-keyword publication tests stay green, the published success/error slices still resolve to `14` and `13` fixture cases with the required text-model and helper splits, and the structural string-count probe now passes.
