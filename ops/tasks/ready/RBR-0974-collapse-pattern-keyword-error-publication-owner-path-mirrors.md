# RBR-0974: Collapse pattern-keyword-error publication owner-path mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored raw pattern keyword-error publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 10-row fixture-to-direct mapping instead of retyping it across the selector and assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer hard-codes multiple mirrored case-id inventories for the same raw pattern keyword-error publication slice inside `_PATTERN_KEYWORD_ERROR_CASE_IDS` and `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()`:
  - the published `str` fixture case-id tuple;
  - the published `bytes` fixture case-id tuple;
  - the full published fixture case-id tuple; and
  - the full selected direct-case tuple.
- Replace those mirrors with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - prefer a tuple of `(fixture_case_id, direct_case)` rows, a tiny frozen dataclass wrapper around that same pair, or an equivalent file-local representation;
  - derive the text-model subsets, full fixture order, and selected direct-case order from that one canonical surface instead of retyping the same publication slice;
  - keep the cleanup scoped to the pattern keyword-error slice instead of widening into the adjacent wrong-text-model publication lane unless a strictly smaller file-local helper serves both without adding new machinery; and
  - do not add a shared helper module, selector registry, or checked-in data layer.
- Preserve the current live raw pattern keyword-error publication contract exactly:
  - `_published_pattern_type_error_fixture_cases(_PATTERN_KEYWORD_ERROR_CASE_IDS)` still resolves to `10` published fixture rows;
  - the published text-model split stays `Counter({"str": 5, "bytes": 5})`;
  - the published helper split stays `Counter({"split": 2, "sub": 4, "subn": 4})`;
  - the full published fixture order still stays:
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
  - the published `str` fixture ids still stay:
    - `workflow-pattern-split-duplicate-maxsplit-keyword-str`
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-after-positional-count-str`
    - `workflow-pattern-sub-count-alias-keyword-str`
  - the published `bytes` fixture ids still stay:
    - `workflow-pattern-split-unexpected-keyword-bytes`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-pattern-subn-count-alias-keyword-bytes`
  - the selected direct-case order still stays:
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
  - the published fixture order and selected direct-case order still stay aligned through the same signature matching that covers the existing `BOUND_PATTERN_TYPE_ERROR_CASES` slice; and
  - do not widen this cleanup into wrong-text-model publication, module-keyword publication, compiled-pattern publication, or benchmark/report plumbing.
- The structural duplication reduction must be visible in the file:
  - the raw occurrence count of `"workflow-pattern-split-duplicate-maxsplit-keyword-str",` drops to at most `1`;
  - the raw occurrence count of `"workflow-pattern-subn-count-alias-keyword-bytes",` drops to at most `1`;
  - the raw occurrence count of `"pattern-split-duplicate-maxsplit-keyword-str",` drops to at most `2`; and
  - the raw occurrence count of `"pattern-subn-count-alias-keyword-bytes",` drops to at most `2`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    _PATTERN_KEYWORD_ERROR_CASE_IDS,
    _fixture_cases_for_text_model,
    _published_pattern_type_error_fixture_cases,
)

published = _published_pattern_type_error_fixture_cases(_PATTERN_KEYWORD_ERROR_CASE_IDS)

assert len(published) == 10
assert Counter(case.text_model for case in published) == Counter({"str": 5, "bytes": 5})
assert Counter(case.helper for case in published) == Counter(
    {
        "split": 2,
        "sub": 4,
        "subn": 4,
    }
)
assert tuple(case.case_id for case in published) == (
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
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "str")) == (
    "workflow-pattern-split-duplicate-maxsplit-keyword-str",
    "workflow-pattern-sub-duplicate-count-keyword-str",
    "workflow-pattern-sub-unexpected-keyword-str",
    "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
    "workflow-pattern-sub-count-alias-keyword-str",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "bytes")) == (
    "workflow-pattern-split-unexpected-keyword-bytes",
    "workflow-pattern-subn-duplicate-count-keyword-bytes",
    "workflow-pattern-subn-unexpected-keyword-bytes",
    "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
    "workflow-pattern-subn-count-alias-keyword-bytes",
)

print("ok", len(published))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count('"workflow-pattern-split-duplicate-maxsplit-keyword-str",') <= 1
assert text.count('"workflow-pattern-subn-count-alias-keyword-bytes",') <= 1
assert text.count('"pattern-split-duplicate-maxsplit-keyword-str",') <= 2
assert text.count('"pattern-subn-count-alias-keyword-bytes",') <= 2

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0974` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` are clear of reserved future ids `RBR-0974` through `RBR-0977` in this run; and
  - the tracked task files currently end at `RBR-0973-catch-up-pattern-search-verbose-regression-sextet.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`2 passed, 1431 deselected`);
  - the publication-count probe in Verification currently passes (`ok 10`), proving the live owner path already resolves to the expected 10-row surface with the current text-model and helper counts; and
  - the structural literal-count probe in Verification currently fails because the same pattern keyword-error publication slice is still mirrored across `_PATTERN_KEYWORD_ERROR_CASE_IDS` and the assertion test instead of deriving from one canonical owner-path surface.
