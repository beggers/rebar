# RBR-0968: Collapse module-keyword publication owner-path mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored raw module-keyword publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 14-row fixture-to-direct mapping instead of retyping it across the publication selector and assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer hard-codes four independent mirrored case-id inventories for the same raw module-keyword publication slice inside `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()`:
  - the `str` fixture case-id tuple;
  - the `bytes` fixture case-id tuple;
  - the full published fixture case-id tuple; and
  - the full selected direct-case tuple.
- Replace those mirrors with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - prefer a tuple of `(fixture_case_id, direct_case)` rows, a tiny frozen dataclass wrapper around that same pair, or an equivalent file-local representation;
  - derive the text-model subsets, full fixture order, and selected direct-case order from that one canonical surface instead of retyping the same publication slice multiple times; and
  - do not add a shared helper module, selector registry, or checked-in data layer.
- Preserve the current live raw module-keyword publication contract exactly:
  - `_published_module_keyword_fixture_cases()` still resolves to `14` published fixture rows;
  - the published text-model split stays `Counter({"str": 6, "bytes": 8})`;
  - the published helper split stays `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`;
  - the published `str` fixture ids stay:
    - `workflow-module-search-flags-keyword-str`
    - `workflow-module-fullmatch-flags-keyword-str`
    - `workflow-module-sub-count-keyword-str`
    - `workflow-module-sub-count-indexlike-str`
    - `workflow-module-sub-count-bool-false-str`
    - `workflow-module-sub-count-bool-true-str`
  - the published `bytes` fixture ids stay:
    - `workflow-module-match-flags-keyword-bytes`
    - `workflow-module-split-maxsplit-keyword-bytes`
    - `workflow-module-split-maxsplit-indexlike-bytes`
    - `workflow-module-split-maxsplit-bool-false-bytes`
    - `workflow-module-subn-count-keyword-bytes`
    - `workflow-module-subn-count-indexlike-bytes`
    - `workflow-module-subn-count-bool-false-bytes`
    - `workflow-module-subn-count-bool-true-bytes`
  - the published fixture order and selected direct-case order still stay aligned through the same signature matching that covers the existing `MODULE_KEYWORD_CALL_CASES` slice; and
  - `test_module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on()` stays green without widening this cleanup into positional-indexlike, keyword-error, or compiled-pattern publication logic.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    _fixture_cases_for_text_model,
    _published_module_keyword_fixture_cases,
)

published = _published_module_keyword_fixture_cases()

assert len(published) == 14
assert Counter(case.text_model for case in published) == Counter(
    {"str": 6, "bytes": 8}
)
assert Counter(case.helper for case in published) == Counter(
    {
        "search": 1,
        "match": 1,
        "fullmatch": 1,
        "split": 3,
        "sub": 4,
        "subn": 4,
    }
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "str")) == (
    "workflow-module-search-flags-keyword-str",
    "workflow-module-fullmatch-flags-keyword-str",
    "workflow-module-sub-count-keyword-str",
    "workflow-module-sub-count-indexlike-str",
    "workflow-module-sub-count-bool-false-str",
    "workflow-module-sub-count-bool-true-str",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "bytes")) == (
    "workflow-module-match-flags-keyword-bytes",
    "workflow-module-split-maxsplit-keyword-bytes",
    "workflow-module-split-maxsplit-indexlike-bytes",
    "workflow-module-split-maxsplit-bool-false-bytes",
    "workflow-module-subn-count-keyword-bytes",
    "workflow-module-subn-count-indexlike-bytes",
    "workflow-module-subn-count-bool-false-bytes",
    "workflow-module-subn-count-bool-true-bytes",
)

print("ok", len(published))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count('"workflow-module-search-flags-keyword-str",') == 1
assert text.count('"workflow-module-subn-count-bool-true-bytes",') == 1
assert text.count('"module-search-flags-keyword-str",') == 1
assert text.count('"module-match-flags-keyword-bytes",') == 1

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0968` is the next available task id in the current checkout:
  - `rg -n 'RBR-0968|RBR-0969|RBR-0970|RBR-0971|RBR-0972' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0967-catch-up-pattern-window-keyword-complement-quartet.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`2 passed, 1423 deselected`);
  - the publication-surface probe in Verification currently passes (`ok 14`), proving the live owner path already resolves to the expected 14-row surface with the current text-model and helper counts; and
  - the structural probe in Verification currently fails only because `tests/python/test_module_workflow_parity_suite.py` still repeats representative raw module-keyword fixture and direct case ids for the same owner path instead of deriving them from one canonical publication surface.

## Completion
- Landed a file-local `ModuleKeywordPublicationOwnerPathRow` owner-path surface in `tests/python/test_module_workflow_parity_suite.py` and routed both `_published_module_keyword_fixture_cases()` and the module-keyword publication assertion through it, so the repeated fixture/direct inventories now derive from one canonical 14-row slice.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
  - the publication-count probe from this task (`ok 14`)
  - the structural literal-count probe from this task (`ok`)
