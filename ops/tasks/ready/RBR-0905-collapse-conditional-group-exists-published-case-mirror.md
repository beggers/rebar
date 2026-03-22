# RBR-0905: Collapse the conditional-group-exists published-case mirror

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `PUBLISHED_CASES` flattening tuple from `tests/python/test_conditional_group_exists_parity_suite.py`, so the conditional parity owner derives its case-id lookup surface directly from the canonical published fixture bundles it already loads.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` no longer defines `PUBLISHED_CASES`:
  - delete the top-level flattened tuple instead of replacing it with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live iterator or selector built directly from `FIXTURE_BUNDLES` rather than another cached published-case mirror.
- The conditional parity owner data comes from the live published bundle surface instead of the deleted flattening layer:
  - `CASES_BY_ID` is built directly from `FIXTURE_BUNDLES` / `bundle.cases` rather than from `PUBLISHED_CASES`; and
  - the current `BASE_*`, `QUANTIFIED_*`, `NESTED_OR_ALTERNATION_*`, and `MATCH_API_CASES` selectors preserve their current case ids, pattern coverage, and ordering while sourcing through the existing bundle-owned data path.
- Route the current owner-path lookups through the live bundle-backed selector instead of the deleted mirror:
  - `MATCH_API_CASES`;
  - the compile metadata assertions that read `CASES_BY_ID[...]`; and
  - any other reads of `PUBLISHED_CASES` or `CASES_BY_ID` in `tests/python/test_conditional_group_exists_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change fixture contents, manifest order, selected case ids, parity expectations, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirror over introducing another shared support module, another selector registry, or another owner-local sidecar table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '^PUBLISHED_CASES = ' tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Keep the change limited to the residual published-case flattening mirror in `tests/python/test_conditional_group_exists_parity_suite.py`. Do not widen into conditional behavior changes, fixture rewrites, shared parity-support refactors, benchmark work, or report regeneration in this run.
- Preserve the current published conditional frontier exactly. The point is to delete one owner-local representation layer, not to reinterpret which conditional rows stay published or how their direct tests behave.

## Notes
- `RBR-0905` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0905|RBR-0906|RBR-0907' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no tracked reservation or existing task for `RBR-0905`.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.45s`);
  - `bash -lc "! rg -n '^PUBLISHED_CASES = ' tests/python/test_conditional_group_exists_parity_suite.py"` currently fails exactly on the remaining mirror at line `64`; and
  - `tests/python/test_conditional_group_exists_parity_suite.py` already keeps `FIXTURE_BUNDLES` and `FIXTURE_BUNDLES_BY_MANIFEST_ID` as the canonical published conditional ownership path, so the flattened `PUBLISHED_CASES` tuple is a redundant second representation rather than missing owner data.
