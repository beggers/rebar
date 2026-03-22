# RBR-0970: Collapse module-keyword-error publication owner-path mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored raw module keyword-error publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 13-row fixture-to-direct mapping instead of retyping it across the publication selector and assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer hard-codes multiple mirrored case-id inventories for the same raw module keyword-error publication slice inside `_published_module_keyword_error_fixture_cases()` and `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()`:
  - the full published direct-case id tuple;
  - the full published fixture-case id tuple;
  - the `str` fixture-case id tuple;
  - the `bytes` fixture-case id tuple; and
  - the full selected direct-case id tuple.
- Replace those mirrors with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - prefer a tuple of `(fixture_case_id, direct_case)` rows, a tiny frozen dataclass wrapper around that same pair, or an equivalent file-local representation;
  - derive the text-model subsets, full fixture order, and selected direct-case order from that one canonical surface instead of retyping the same publication slice multiple times; and
  - do not add a shared helper module, selector registry, or checked-in data layer.
- Preserve the current live raw module keyword-error publication contract exactly:
  - `_published_module_keyword_error_fixture_cases()` still resolves to `13` published fixture rows;
  - the published text-model split stays `Counter({"str": 8, "bytes": 5})`;
  - the published helper split stays `Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})`;
  - the published fixture order stays:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
    - `workflow-module-sub-count-alias-keyword`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-module-subn-count-alias-keyword-bytes`
  - the published `str` fixture ids stay:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
    - `workflow-module-sub-count-alias-keyword`
  - the published `bytes` fixture ids stay:
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-module-subn-count-alias-keyword-bytes`
  - the selected direct-case order still stays:
    - `module-search-duplicate-flags-keyword`
    - `module-split-duplicate-maxsplit-keyword`
    - `module-split-unexpected-keyword`
    - `module-split-unexpected-keyword-bytes`
    - `module-sub-duplicate-count-keyword`
    - `module-fullmatch-unexpected-keyword`
    - `module-sub-unexpected-keyword`
    - `module-sub-unexpected-keyword-after-positional-count`
    - `module-sub-count-alias-keyword`
    - `module-subn-duplicate-count-keyword-bytes`
    - `module-subn-unexpected-keyword-bytes`
    - `module-subn-unexpected-keyword-after-positional-count-bytes`
    - `module-subn-count-alias-keyword-bytes`
  - the published fixture order and selected direct-case order still stay aligned through the same signature matching that covers the existing `MODULE_KEYWORD_ERROR_CASES` slice; and
  - do not widen this cleanup into module keyword success rows, positional-indexlike publication, compiled-pattern publication, or benchmark/report plumbing.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    _fixture_cases_for_text_model,
    _published_module_keyword_error_fixture_cases,
)

published = _published_module_keyword_error_fixture_cases()

assert len(published) == 13
assert Counter(case.text_model for case in published) == Counter({"str": 8, "bytes": 5})
assert Counter(case.helper for case in published) == Counter(
    {
        "search": 1,
        "split": 3,
        "sub": 4,
        "fullmatch": 1,
        "subn": 4,
    }
)
assert tuple(case.case_id for case in published) == (
    "workflow-module-search-duplicate-flags-keyword",
    "workflow-module-split-duplicate-maxsplit-keyword",
    "workflow-module-split-unexpected-keyword",
    "workflow-module-split-unexpected-keyword-bytes",
    "workflow-module-sub-duplicate-count-keyword",
    "workflow-module-fullmatch-unexpected-keyword",
    "workflow-module-sub-unexpected-keyword",
    "workflow-module-sub-unexpected-keyword-after-positional-count",
    "workflow-module-sub-count-alias-keyword",
    "workflow-module-subn-duplicate-count-keyword-bytes",
    "workflow-module-subn-unexpected-keyword-bytes",
    "workflow-module-subn-unexpected-keyword-after-positional-count-bytes",
    "workflow-module-subn-count-alias-keyword-bytes",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "str")) == (
    "workflow-module-search-duplicate-flags-keyword",
    "workflow-module-split-duplicate-maxsplit-keyword",
    "workflow-module-split-unexpected-keyword",
    "workflow-module-sub-duplicate-count-keyword",
    "workflow-module-fullmatch-unexpected-keyword",
    "workflow-module-sub-unexpected-keyword",
    "workflow-module-sub-unexpected-keyword-after-positional-count",
    "workflow-module-sub-count-alias-keyword",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "bytes")) == (
    "workflow-module-split-unexpected-keyword-bytes",
    "workflow-module-subn-duplicate-count-keyword-bytes",
    "workflow-module-subn-unexpected-keyword-bytes",
    "workflow-module-subn-unexpected-keyword-after-positional-count-bytes",
    "workflow-module-subn-count-alias-keyword-bytes",
)

print("ok", len(published))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count('"workflow-module-search-duplicate-flags-keyword",') == 1
assert text.count('"workflow-module-subn-count-alias-keyword-bytes",') == 1
assert text.count('"module-search-duplicate-flags-keyword",') == 1
assert text.count('"module-subn-count-alias-keyword-bytes",') == 1

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0970` is the next available task id in the current checkout:
  - `rg -n 'RBR-0970|RBR-0971|RBR-0972|RBR-0973|RBR-0974' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 10` currently ends at `RBR-0969-catch-up-pattern-findall-finditer-window-keyword-quartet.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'` currently passes (`1 passed, 1432 deselected`);
  - the publication-count probe in Verification currently passes (`ok 13`), proving the live owner path already resolves to the expected 13-row surface with the current text-model and helper counts; and
  - the structural literal-count probe in Verification currently fails only because `tests/python/test_module_workflow_parity_suite.py` still repeats representative raw module keyword-error fixture and direct case ids for the same owner path instead of deriving them from one canonical publication surface.
