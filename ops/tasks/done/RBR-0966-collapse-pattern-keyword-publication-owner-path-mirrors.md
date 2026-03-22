# RBR-0966: Collapse pattern-keyword publication owner-path mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored pattern-keyword publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 27-row fixture-to-direct mapping instead of retyping it across the publication selector and assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer hard-codes four independent mirrored case-id inventories for the same pattern-keyword publication slice inside `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()`:
  - the `str` fixture case-id tuple;
  - the `bytes` fixture case-id tuple;
  - the full published fixture case-id tuple; and
  - the full selected direct case-id tuple.
- Replace those mirrors with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - it may be a tiny frozen dataclass tuple, a tuple of `(fixture_case_id, direct_case_id, text_model)` rows, or an equivalent file-local representation;
  - derive the text-model subsets, full fixture order, and full selected-direct order from that one canonical surface instead of retyping the same ids multiple times; and
  - do not add a shared helper module, selector registry, or checked-in data layer.
- Preserve the current live pattern-keyword publication contract exactly:
  - `_published_pattern_keyword_fixture_cases()` still resolves to `27` published fixture rows;
  - the published text-model split stays `Counter({"str": 15, "bytes": 12})`;
  - the published helper split stays `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`;
  - the first five published `str` fixture ids stay:
    - `workflow-pattern-search-str-pos-keyword`
    - `workflow-pattern-search-str-bool-endpos-keyword`
    - `workflow-pattern-search-str-pos-indexlike`
    - `workflow-pattern-match-str-pos-keyword`
    - `workflow-pattern-match-str-bool-pos-keyword`
  - the last four published `bytes` fixture ids stay:
    - `workflow-pattern-sub-count-keyword-bytes`
    - `workflow-pattern-sub-count-indexlike-bytes`
    - `workflow-pattern-sub-count-bool-false-bytes`
    - `workflow-pattern-sub-count-bool-true-bytes`
  - the published fixture order and selected direct-case order still stay aligned through the same signature matching that covers the existing `PATTERN_KEYWORD_CALL_CASES` slice; and
  - `test_pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on()` stays green without widening this cleanup into adjacent keyword-error, wrong-text-model, or positional-indexlike publication logic.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    _fixture_cases_for_text_model,
    _published_pattern_keyword_fixture_cases,
)

published = _published_pattern_keyword_fixture_cases()

assert len(published) == 27
assert Counter(case.text_model for case in published) == Counter(
    {"str": 15, "bytes": 12}
)
assert Counter(case.helper for case in published) == Counter(
    {
        "search": 5,
        "match": 3,
        "fullmatch": 2,
        "findall": 3,
        "finditer": 3,
        "split": 3,
        "sub": 4,
        "subn": 4,
    }
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "str")[:5]) == (
    "workflow-pattern-search-str-pos-keyword",
    "workflow-pattern-search-str-bool-endpos-keyword",
    "workflow-pattern-search-str-pos-indexlike",
    "workflow-pattern-match-str-pos-keyword",
    "workflow-pattern-match-str-bool-pos-keyword",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(published, "bytes")[-4:]) == (
    "workflow-pattern-sub-count-keyword-bytes",
    "workflow-pattern-sub-count-indexlike-bytes",
    "workflow-pattern-sub-count-bool-false-bytes",
    "workflow-pattern-sub-count-bool-true-bytes",
)

print("ok", len(published))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count('"workflow-pattern-search-str-pos-keyword",') == 1
assert text.count('"workflow-pattern-subn-count-bool-true-str",') == 1
assert text.count('"pattern-search-pos-keyword-str",') == 1
assert text.count('"pattern-subn-count-bool-true-str",') == 1

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0966` is the next available task id in the current checkout:
  - `rg -n 'RBR-0966|RBR-0967|RBR-0968|RBR-0969|RBR-0970' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved frontier match in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 15` currently ends at `RBR-0965-catch-up-pattern-window-wrong-text-model-boundary-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`2 passed, 1423 deselected`);
  - the publication-surface probe in Verification currently passes (`ok 27`), proving the live owner path already resolves to the expected 27-row surface with the current text-model and helper counts; and
  - the structural probe in Verification currently fails only because `tests/python/test_module_workflow_parity_suite.py` still repeats representative fixture/direct ids for the same owner path instead of deriving them from one canonical publication surface.

## Completion
- Landed a file-local `PatternKeywordPublicationOwnerPathRow` owner-path surface in `tests/python/test_module_workflow_parity_suite.py` and routed the pattern-keyword publication assertions, the bundle-contract fixture-id subset, and the bool-count follow-on check through it so the repeated fixture/direct inventories collapse to one canonical slice.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
  - the publication-count probe from this task (`ok 27`)
  - the structural literal-count probe from this task (`ok`)
