# RBR-0901: Collapse the grouped-capture published-case flattening mirror

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `PUBLISHED_CASES` flattening tuple from `tests/python/test_grouped_capture_parity_suite.py`, so the grouped-capture owner suite derives its compile, module, pattern, and case-id lookup surfaces directly from the canonical published fixture bundles it already loads.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` no longer defines `PUBLISHED_CASES`:
  - delete the top-level flattened tuple instead of replacing it with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live selector or iterator built directly from `FIXTURE_BUNDLES` rather than another cached published-case mirror.
- The grouped-capture owner data comes from the live published bundle surface instead of the deleted flattening layer:
  - `CASES_BY_ID` is built directly from `FIXTURE_BUNDLES` / `bundle.cases` rather than from `PUBLISHED_CASES`;
  - `MODULE_CASES` and `PATTERN_CASES` preserve the current published case-id order while sourcing directly from the live bundle-owned case stream; and
  - `COMPILE_CASES` may continue to use `_compile_cases(...)`, but its input comes from the live published bundle data and preserves the current compile ids, patterns, and flags for the grouped-capture surface.
- Route the current grouped-capture owner setup through the live bundle-backed selectors instead of the deleted mirror:
  - `test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier()`;
  - `test_pattern_bounds_cases_stay_anchored_to_grouped_capture_patterns()`; and
  - any other reads of `PUBLISHED_CASES` in `tests/python/test_grouped_capture_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change fixture contents, manifest order, selected case ids, parity expectations, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirror over introducing another shared support module, another selector registry, or another owner-local sidecar table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `bash -lc "! rg -n '^PUBLISHED_CASES = ' tests/python/test_grouped_capture_parity_suite.py"`

## Constraints
- Keep the change limited to the residual published-case flattening mirror in `tests/python/test_grouped_capture_parity_suite.py`. Do not widen into grouped-capture behavior changes, fixture rewrites, shared parity-support refactors, benchmark work, or report regeneration in this run.
- Preserve the current grouped-capture published frontier exactly. The point is to delete one owner-local representation layer, not to reinterpret which grouped-capture rows stay published or how their direct tests behave.

## Notes
- `RBR-0901` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0901|RBR-0902|RBR-0903' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` found no tracked reservation or existing task for `RBR-0901`.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`432 passed in 0.31s`);
  - `bash -lc "! rg -n '^PUBLISHED_CASES = ' tests/python/test_grouped_capture_parity_suite.py"` currently fails exactly on the remaining mirror at line `134`; and
  - `tests/python/test_grouped_capture_parity_suite.py` already keeps `FIXTURE_BUNDLES` plus `FIXTURE_BUNDLES_BY_MANIFEST_ID` as the canonical published grouped-capture ownership path, so the flattened `PUBLISHED_CASES` tuple is a redundant second representation rather than missing owner data.
