# RBR-0893: Collapse residual module-workflow published collection helper buckets

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the remaining published collection helper-bucket mirrors in `tests/python/test_module_workflow_parity_suite.py`, so the module-workflow collection owner derives its published module/pattern helper slices directly from the live fixture-backed collection cases instead of keeping two extra top-level dictionaries.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines `PUBLISHED_MODULE_COLLECTION_CASES_BY_HELPER` or `PUBLISHED_PATTERN_COLLECTION_CASES_BY_HELPER`:
  - delete both mirrored dictionaries instead of replacing them with another top-level mirror;
  - derive the published module-side and pattern-side helper slices directly from `PUBLISHED_COLLECTION_SUCCESS_FIXTURE_CASES` through tiny file-local selectors or conversion helpers; and
  - preserve the current published helper ordering for `split`, `findall`, and `finditer`.
- `MODULE_COLLECTION_CASES` and `PATTERN_COLLECTION_CASES` keep the same effective case order and supplemental direct cases, but stop splatting the deleted published-helper dictionaries:
  - keep the existing published fixture-backed rows ahead of the direct supplemental cases for each helper family; and
  - do not change case ids, helper coverage, text-model coverage, bounds, or collection semantics.
- `test_literal_collection_direct_test_buckets_cover_selected_frontier()` stops reading the deleted published-helper dictionaries:
  - build the `"module-split"`, `"pattern-split"`, `"module-findall"`, `"pattern-findall"`, `"module-finditer"`, and `"pattern-finditer"` case-id buckets from the same live fixture-derived helper selectors used by the owner data above; and
  - keep the existing type-error bucket coverage derived from `PUBLISHED_COLLECTION_TYPE_ERROR_FIXTURE_CASES`.
- Keep this cleanup structural only:
  - do not change `COLLECTION_REPLACEMENT_BUNDLE`, `PUBLISHED_COLLECTION_FIXTURE_CASES`, `PUBLISHED_COLLECTION_SUCCESS_FIXTURE_CASES`, `PUBLISHED_COLLECTION_TYPE_ERROR_FIXTURE_CASES`, fixture contents, parity expectations, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirrored helper-bucket layer over introducing another shared abstraction or another detached registry.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'`
  - `bash -lc "! rg -n '^PUBLISHED_(MODULE|PATTERN)_COLLECTION_CASES_BY_HELPER = \\{$' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the change limited to the residual published collection helper buckets in the module-workflow parity owner. Do not widen into bounded-wildcard cleanup, compiled-pattern workflow cleanup, fixture-content edits, or new shared helper modules in this run.
- Preserve the current published collection frontier exactly; the point is to delete one more mirrored owner layer, not to reinterpret which collection cases are published or supplemental.

## Notes
- `RBR-0893` is the next available architecture task id in the current checkout:
  - `RBR-0892` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0892-publish-module-workflow-pattern-match-bytes-window-indexlike-pair.md`; and
  - `rg -n 'RBR-0893|RBR-0894|RBR-0895' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` found no tracked reservation or existing task for `RBR-0893`.
- There is no blocked architecture task to reopen or normalize first because `/home/ubuntu/rebar/ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'` currently passes (`15 passed, 1208 deselected`);
  - `rg -n '^PUBLISHED_(MODULE|PATTERN)_COLLECTION_CASES_BY_HELPER = \\{$' tests/python/test_module_workflow_parity_suite.py` currently reports the residual mirrors at lines `1097` and `1105`; and
  - those dictionaries are only used to feed `MODULE_COLLECTION_CASES`, `PATTERN_COLLECTION_CASES`, and `test_literal_collection_direct_test_buckets_cover_selected_frontier()`, which keeps this cleanup bounded to one owner file.

## Completion
- Deleted `PUBLISHED_MODULE_COLLECTION_CASES_BY_HELPER` and `PUBLISHED_PATTERN_COLLECTION_CASES_BY_HELPER` from `tests/python/test_module_workflow_parity_suite.py`.
- Added two small fixture-backed selectors, `_published_module_collection_cases_for_helper(...)` and `_published_pattern_collection_cases_for_helper(...)`, and rewired `MODULE_COLLECTION_CASES`, `PATTERN_COLLECTION_CASES`, and `test_literal_collection_direct_test_buckets_cover_selected_frontier()` to use them directly.
- Preserved the published `split`, `findall`, and `finditer` ordering and left the supplemental direct cases and type-error coverage unchanged.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'`
  - `bash -lc "! rg -n '^PUBLISHED_(MODULE|PATTERN)_COLLECTION_CASES_BY_HELPER = \\{$' tests/python/test_module_workflow_parity_suite.py"`
