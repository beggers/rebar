# RBR-1018: Collapse pattern-keyword bool-count complement sidecar onto owner-path rows

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached pattern-keyword bool-count complement sidecar from `tests/python/test_module_workflow_parity_suite.py` so the follow-on balance check derives its expected published slice from the canonical pattern-keyword owner-path rows instead of carrying a second local tuple of the same direct cases.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads `PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES`.
- Replace that sidecar with one file-local owner-path-derived route, or a strictly smaller equivalent, that keeps `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS` as the canonical published surface for the same four bool-count complement rows:
  - `workflow-pattern-sub-count-bool-false-bytes`
  - `workflow-pattern-sub-count-bool-true-bytes`
  - `workflow-pattern-subn-count-bool-false-str`
  - `workflow-pattern-subn-count-bool-true-str`
- Keep the direct-case follow-on contract exact while deleting the detached tuple:
  - `test_pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on()` still proves the filtered `PATTERN_KEYWORD_CALL_CASES` projection resolves, in order, to:
    - `("pattern-sub-count-bool-false-bytes", "sub", b"abc", (("count", "bool", False),))`
    - `("pattern-sub-count-bool-true-bytes", "sub", b"abc", (("count", "bool", True),))`
    - `("pattern-subn-count-bool-true-str", "subn", "abc", (("count", "bool", True),))`
    - `("pattern-subn-count-bool-false-str", "subn", "abc", (("count", "bool", False),))`
  - the published owner-path subset above remains aligned with those same four direct cases; and
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()` stays green without widening this cleanup into keyword-error, wrong-text-model, positional-indexlike, module-keyword, or compiled-pattern publication logic.
- Keep the cleanup structural and file-local:
  - prefer deriving bool-count complement membership from `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS` and then selecting the ordered direct cases from `PATTERN_KEYWORD_CALL_CASES` over introducing another detached tuple, registry, or helper module;
  - keep `_workflow_bool_count_complement_projection(...)` and the existing owner-path helpers as the canonical lower-level contract surfaces unless a strictly smaller file-local successor preserves the same coverage;
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files; and
  - do not widen this run into collection-helper cleanup, bounded-wildcard publication, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    PATTERN_KEYWORD_CALL_CASES,
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _workflow_bool_count_complement_projection,
    _workflow_keyword_kwargs_signature,
)

projection = lambda case: (
    case.case_id,
    case.helper,
    case.pattern,
    _workflow_keyword_kwargs_signature(case.kwargs),
)
rows = tuple(
    row
    for row in PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS
    if row.direct_case.helper in {"sub", "subn"}
    if _workflow_keyword_kwargs_signature(row.direct_case.kwargs)
    in {
        (("count", "bool", False),),
        (("count", "bool", True),),
    }
)

assert tuple(row.fixture_case_id for row in rows) == (
    "workflow-pattern-sub-count-bool-false-bytes",
    "workflow-pattern-sub-count-bool-true-bytes",
    "workflow-pattern-subn-count-bool-false-str",
    "workflow-pattern-subn-count-bool-true-str",
)
assert _workflow_bool_count_complement_projection(
    PATTERN_KEYWORD_CALL_CASES,
    projection,
    helpers=frozenset({"sub", "subn"}),
) == (
    ("pattern-sub-count-bool-false-bytes", "sub", b"abc", (("count", "bool", False),)),
    ("pattern-sub-count-bool-true-bytes", "sub", b"abc", (("count", "bool", True),)),
    ("pattern-subn-count-bool-true-str", "subn", "abc", (("count", "bool", True),)),
    ("pattern-subn-count-bool-false-str", "subn", "abc", (("count", "bool", False),)),
)
print("ok")
PY`
- `bash -lc "! rg -n '^PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the remaining sidecar tuple over introducing another detached selector layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- `RBR-1018` is the next available unreserved task id in the current checkout:
  - a repo-local `python3` scan over `ops/state/backlog.md`, `ops/state/current_status.md`, and all task queues reported `1018` as the first unused `RBR-` number in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES` at line `2389`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` currently passes (`2 passed, 1449 deselected`);
  - the owner-path/direct-case probe in Verification currently passes (`ok`); and
  - `rg -n '^PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES = ' tests/python/test_module_workflow_parity_suite.py` currently reports that one residual sidecar declaration, so the structural no-match check fails exactly on this cleanup.
- This cleanup is distinct from the earlier pattern-keyword owner-path work:
  - `RBR-0966` collapsed the main pattern-keyword publication inventories onto `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`; and
  - `RBR-1007` collapsed the shared bool-count complement projection glue across the adjacent balance tests.
  - The remaining detached `PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES` tuple is the next bounded mirror still living on that same owner-path surface.
