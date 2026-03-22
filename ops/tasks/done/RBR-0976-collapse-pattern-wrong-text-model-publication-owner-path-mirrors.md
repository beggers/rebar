# RBR-0976: Collapse pattern wrong-text-model publication owner-path mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored direct-`Pattern` wrong-text-model publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 6-row fixture-to-direct mapping instead of retyping it across a dedicated case-id tuple, two one-off selector helpers, and the publication assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer carries a dedicated wrong-text-model mirror stack that exists only for this one publication slice:
  - remove `_PATTERN_WRONG_TEXT_MODEL_CASE_IDS`;
  - remove `_published_pattern_type_error_fixture_cases(...)`; and
  - remove `_selected_pattern_type_error_direct_cases(...)`.
- Replace that mirror stack with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - prefer reusing the existing `PatternTypeErrorOwnerPathRow` plus `_published_pattern_type_error_owner_path_fixture_cases(...)` and `_selected_pattern_type_error_owner_path_direct_cases(...)` helpers rather than introducing another representation;
  - derive the published `str` subset, published `bytes` subset, full fixture order, and selected direct-case order from that one canonical wrong-text-model owner path instead of retyping those inventories in the test body; and
  - do not add a shared helper module, selector registry, or checked-in data layer.
- Preserve the current live direct-`Pattern` wrong-text-model publication contract exactly:
  - the published fixture order still stays:
    - `workflow-pattern-search-str-pattern-on-bytes-string`
    - `workflow-pattern-match-bytes-pattern-on-str-string`
    - `workflow-pattern-fullmatch-str-pattern-on-bytes-string`
    - `workflow-pattern-split-str-pattern-on-bytes-string`
    - `workflow-pattern-sub-str-pattern-on-bytes-string`
    - `workflow-pattern-subn-bytes-pattern-on-str-string`
  - the published `str` fixture ids still stay:
    - `workflow-pattern-search-str-pattern-on-bytes-string`
    - `workflow-pattern-fullmatch-str-pattern-on-bytes-string`
    - `workflow-pattern-split-str-pattern-on-bytes-string`
    - `workflow-pattern-sub-str-pattern-on-bytes-string`
  - the published `bytes` fixture ids still stay:
    - `workflow-pattern-match-bytes-pattern-on-str-string`
    - `workflow-pattern-subn-bytes-pattern-on-str-string`
  - the selected direct-case order still stays:
    - `pattern-search-str-pattern-on-bytes-string`
    - `pattern-match-bytes-pattern-on-str-string`
    - `pattern-fullmatch-str-pattern-on-bytes-string`
    - `pattern-split-str-pattern-on-bytes-string`
    - `pattern-sub-str-pattern-on-bytes-string`
    - `pattern-subn-bytes-pattern-on-str-string`
  - the published fixture slice still resolves to `6` rows;
  - the published text-model split still stays `Counter({"str": 4, "bytes": 2})`;
  - the published helper split still stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`; and
  - the published fixture order and selected direct-case order still stay aligned through the same signature matching that covers the existing `BOUND_PATTERN_TYPE_ERROR_CASES` slice.
- The structural duplication reduction must be visible in the file:
  - `rg -n '^_PATTERN_WRONG_TEXT_MODEL_CASE_IDS =|^def _published_pattern_type_error_fixture_cases\\(|^def _selected_pattern_type_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches; and
  - the raw occurrence count of `"workflow-pattern-search-str-pattern-on-bytes-string",` drops to at most `1`;
  - the raw occurrence count of `"workflow-pattern-subn-bytes-pattern-on-str-string",` drops to at most `1`;
  - the raw occurrence count of `"pattern-search-str-pattern-on-bytes-string",` drops to at most `2`; and
  - the raw occurrence count of `"pattern-subn-bytes-pattern-on-str-string",` drops to at most `2`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases or pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string or pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    _PATTERN_WRONG_TEXT_MODEL_CASE_IDS,
    _fixture_cases_for_text_model,
    _published_pattern_type_error_fixture_cases,
)

published = _published_pattern_type_error_fixture_cases(_PATTERN_WRONG_TEXT_MODEL_CASE_IDS)

assert tuple(case.case_id for case in published) == (
    "workflow-pattern-search-str-pattern-on-bytes-string",
    "workflow-pattern-match-bytes-pattern-on-str-string",
    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
    "workflow-pattern-split-str-pattern-on-bytes-string",
    "workflow-pattern-sub-str-pattern-on-bytes-string",
    "workflow-pattern-subn-bytes-pattern-on-str-string",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "str")) == (
    "workflow-pattern-search-str-pattern-on-bytes-string",
    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
    "workflow-pattern-split-str-pattern-on-bytes-string",
    "workflow-pattern-sub-str-pattern-on-bytes-string",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "bytes")) == (
    "workflow-pattern-match-bytes-pattern-on-str-string",
    "workflow-pattern-subn-bytes-pattern-on-str-string",
)
assert Counter(case.text_model for case in published) == Counter({"str": 4, "bytes": 2})
assert Counter(case.helper for case in published) == Counter(
    {
        "search": 1,
        "match": 1,
        "fullmatch": 1,
        "split": 1,
        "sub": 1,
        "subn": 1,
    }
)

print("ok", len(published))
PY`
- `bash -lc "! rg -n '^_PATTERN_WRONG_TEXT_MODEL_CASE_IDS =|^def _published_pattern_type_error_fixture_cases\\(|^def _selected_pattern_type_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count('"workflow-pattern-search-str-pattern-on-bytes-string",') <= 1
assert text.count('"workflow-pattern-subn-bytes-pattern-on-str-string",') <= 1
assert text.count('"pattern-search-str-pattern-on-bytes-string",') <= 2
assert text.count('"pattern-subn-bytes-pattern-on-str-string",') <= 2

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0976` is the next available task id in the current checkout:
  - `rg -n 'RBR-0976|RBR-0977|RBR-0978|RBR-0979|RBR-0980' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0975-catch-up-pattern-fullmatch-verbose-regression-sextet.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases or pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string or pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'` currently passes (`19 passed, 1414 deselected`);
  - the publication-count probe in Verification currently passes (`ok 6`), proving the live helper stack already resolves to the expected 6-row surface with the current text-model and helper counts; and
  - `rg -n '^_PATTERN_WRONG_TEXT_MODEL_CASE_IDS =|^def _published_pattern_type_error_fixture_cases\\(|^def _selected_pattern_type_error_direct_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the dedicated wrong-text-model mirror stack at lines `2945`, `2955`, and `2970`, while the structural literal-count probe in Verification currently fails because the same owner path is still retyped in both the helper stack and the assertion body.

## Completion
- 2026-03-22: Replaced the wrong-text-model mirror stack with one file-local `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS` tuple in `tests/python/test_module_workflow_parity_suite.py`, deleted `_PATTERN_WRONG_TEXT_MODEL_CASE_IDS` plus the two one-off selector helpers, and derived the published fixture order, `str`/`bytes` subsets, and selected direct-case order from the canonical owner-path rows. Verified with the targeted pytest selector, an owner-path publication-count probe (`ok 6`), the no-match `rg` check for the removed mirror stack, and the raw literal-count probe from this task.
