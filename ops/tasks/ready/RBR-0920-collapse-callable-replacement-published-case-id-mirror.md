# RBR-0920: Collapse callable-replacement published case-id mirror

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `PUBLISHED_CALLABLE_CASE_IDS` tuple from `tests/python/test_callable_replacement_parity_suite.py`, so the callable-replacement owner derives its selected published frontier directly from the live `PUBLISHED_CALLABLE_CASES` rows it already builds instead of caching a second ordered case-id mirror.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` no longer defines or reads `PUBLISHED_CALLABLE_CASE_IDS`:
  - delete the top-level tuple instead of replacing it with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live selector over `PUBLISHED_CALLABLE_CASES` rather than another cached case-id mirror.
- Route the callable-replacement direct-frontier assertion through live owner data instead of the deleted mirror:
  - `test_callable_replacement_direct_test_buckets_cover_selected_frontier()` still keeps the same four bucket labels in the same coverage shape: `shared-module`, `shared-pattern`, `pending-rebar-bytes-module`, and `pending-rebar-bytes-pattern`;
  - the `selected_case_ids` argument now derives directly from the live `PUBLISHED_CALLABLE_CASES` ordering rather than from a cached tuple; and
  - preserve the current published callable frontier exactly, with no added, dropped, or reordered case ids.
- Keep this cleanup structural only:
  - do not change fixture contents, callable replacement behavior, pending/shared case partitioning, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirror over introducing another shared helper module, registry table, or support abstraction.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^PUBLISHED_CALLABLE_CASE_IDS = ' tests/python/test_callable_replacement_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_callable_replacement_parity_suite import FIXTURE_BUNDLES, PUBLISHED_CALLABLE_CASES

live_case_ids = tuple(case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases)
flattened_case_ids = tuple(case.case_id for case in PUBLISHED_CALLABLE_CASES)

assert flattened_case_ids == live_case_ids
print("ok", len(flattened_case_ids))
PY`

## Constraints
- Keep the change limited to `tests/python/test_callable_replacement_parity_suite.py`. Do not widen into fixture manifest edits, shared parity-support refactors, pending-feature parity work, reports, or tracked state files in this run.
- Preserve the current callable-replacement published frontier exactly. The point is to delete one owner-local representation layer, not to reinterpret which published rows define the direct-test coverage surface.

## Notes
- `RBR-0920` is the next available architecture task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 30` currently ends at `RBR-0919-catch-up-pattern-sub-subn-unexpected-keyword-boundary-pair.md`; and
  - `rg -n 'RBR-0920|RBR-0921|RBR-0922|RBR-0923|RBR-0924|RBR-0925|RBR-0926|RBR-0927|RBR-0928|RBR-0929|RBR-0930' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and the latest recorded task-worker runs finished `done`; and
  - the live queue listing is empty in `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2747 passed in 2.06s`);
  - `rg -n '^PUBLISHED_CALLABLE_CASE_IDS = ' tests/python/test_callable_replacement_parity_suite.py` currently finds the remaining mirror at line `1075`; and
  - the task-local live-flattening probe in Acceptance currently passes (`ok 168`), proving the live `FIXTURE_BUNDLES` to `PUBLISHED_CALLABLE_CASES` path already recovers the full ordered published callable frontier without the cached tuple.
