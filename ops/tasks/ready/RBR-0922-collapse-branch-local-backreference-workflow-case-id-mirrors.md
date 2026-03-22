# RBR-0922: Collapse branch-local backreference workflow case-id mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS` tuple and `_SHARED_WORKFLOW_CASE_IDS` set from `tests/python/test_branch_local_backreference_parity_suite.py`, so the branch-local owner derives those same case selections directly from the live whole-manifest bundles and the already-built module/pattern buckets instead of caching second copies of the same ids.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` no longer defines `SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS` or `_SHARED_WORKFLOW_CASE_IDS`:
  - delete both top-level mirrors instead of replacing them with another detached tuple/list/set/map of the same ids; and
  - if helpers remain, keep them as tiny file-local live selectors over `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES`, `MODULE_CASES`, and `PATTERN_CASES` rather than another cached mirror.
- Preserve the current simple-backreference manifest surface exactly while routing it through live owner data:
  - the non-compile rows selected from `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES` still stay ordered as `named-backreference-module-search-str`, `named-backreference-pattern-search-str`, `numbered-backreference-module-search-str`, `numbered-backreference-pattern-search-str`, `numbered-backreference-segment-module-search-str`, then `numbered-backreference-prefix-pattern-search-str`; and
  - `MATCH_CONVENIENCE_CASE_IDS` and `MATCH_GROUP_ACCESS_CASE_IDS` still include that same simple-backreference workflow slice without introducing a second handwritten manifest-id or case-id mirror.
- Preserve the current shared branch-local workflow selection exactly while routing it through live buckets:
  - `WORKFLOW_CASES` still spans the same 78 ordered shared module/pattern rows it covers today;
  - `test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier()` and the `@pytest.mark.parametrize("case", WORKFLOW_CASES, ...)` path keep the same selected frontier and ordering; and
  - do not add, drop, or reorder shared workflow rows while deleting the mirrors.
- Keep this cleanup structural only:
  - do not change fixture contents, parity behavior, pending/shared direct-bytes follow-on routing, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirrors over introducing a new shared support module, registry table, or abstraction layer.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `bash -lc "! rg -n '^(SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS|_SHARED_WORKFLOW_CASE_IDS)\\s*=' tests/python/test_branch_local_backreference_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_branch_local_backreference_parity_suite import (
    MODULE_CASES,
    PATTERN_CASES,
    WHOLE_MANIFEST_BACKREFERENCE_BUNDLES,
    WORKFLOW_CASES,
    _iter_fixture_cases,
)

simple_live = tuple(
    case.case_id
    for bundle in WHOLE_MANIFEST_BACKREFERENCE_BUNDLES
    for case in bundle.cases
    if case.operation != "compile"
)
shared_ids = frozenset(case.case_id for case in (*MODULE_CASES, *PATTERN_CASES))
workflow_live = tuple(
    case.case_id for case in _iter_fixture_cases() if case.case_id in shared_ids
)

assert simple_live == (
    "named-backreference-module-search-str",
    "named-backreference-pattern-search-str",
    "numbered-backreference-module-search-str",
    "numbered-backreference-pattern-search-str",
    "numbered-backreference-segment-module-search-str",
    "numbered-backreference-prefix-pattern-search-str",
)
assert workflow_live == tuple(case.case_id for case in WORKFLOW_CASES)
print("ok", len(simple_live), len(workflow_live))
PY`

## Constraints
- Keep the change limited to `tests/python/test_branch_local_backreference_parity_suite.py`. Do not widen into fixture manifest edits, shared parity-support refactors, follow-on feature work, reports, or tracked state files in this run.
- Preserve the current branch-local backreference frontier exactly. The point is to delete owner-local representation layers, not to reinterpret which rows belong in the shared workflow or match-group-access surfaces.

## Notes
- `RBR-0922` is the next available architecture task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0921-match-pattern-split-duplicate-maxsplit-unexpected-keyword-typeerrors.md`; and
  - `rg -n 'RBR-0922|RBR-0923|RBR-0924|RBR-0925|RBR-0926|RBR-0927|RBR-0928|RBR-0929|RBR-0930' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and no last-cycle anomalies; and
  - the live queue listing is empty in `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - `rg -n '^(SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS|_SHARED_WORKFLOW_CASE_IDS)\\s*=' tests/python/test_branch_local_backreference_parity_suite.py` currently finds the remaining mirrors at lines `93` and `503`; and
  - the task-local live-selector probe in Acceptance currently passes (`ok 6 78`), proving the suite's existing whole-manifest bundles plus module/pattern buckets already recover the same simple workflow slice and ordered shared workflow surface without those cached mirrors.
