# RBR-0895: Collapse residual module-workflow bounded-wildcard case mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining bounded-wildcard published-case mirrors in `tests/python/test_module_workflow_parity_suite.py`, so that owner file derives its published bounded-wildcard slices directly from the live fixture-backed module/compile/pattern case inventories instead of keeping five extra top-level tuple constants.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines these top-level tuple mirrors:
  - `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`
  - `PUBLISHED_BOUNDED_WILDCARD_COMPILE_CASES`
  - `PUBLISHED_BOUNDED_WILDCARD_PATTERN_CASES`
  - `PUBLISHED_BOUNDED_WILDCARD_PATTERN_MATCH_CASES`
  - `PUBLISHED_BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES`
- Derive the same effective published bounded-wildcard slices directly from the existing live owner data:
  - use `MODULE_CALL_CASES`, `COMPILE_CASES_BY_ID`, `PATTERN_CASES_BY_ID`, and the existing `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS` / `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS` selectors or an equivalently direct live path;
  - preserve the current published case ordering for the compile slice and the pattern slice;
  - keep the existing match-vs-collection partition for the pattern slice; and
  - keep the raw module-helper slice limited to the current non-compiled bounded-wildcard `search` / `match` / `fullmatch` rows.
- Route the current bounded-wildcard owners through those live selectors instead of the deleted mirrors:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()`
  - `test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases()`
  - `test_bounded_wildcard_compile_metadata_matches_cpython()`
  - the bounded-wildcard pattern match/helper parametrizations
  - the bounded-wildcard pattern collection/helper parametrizations
  - any adjacent alignment/count assertions that currently read the deleted constants
- Keep this cleanup structural only:
  - do not change `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS`, `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`, fixture contents, selected case ids, direct supplemental bounded-wildcard cases, parity expectations, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirrored tuple layer over adding another shared helper module or another detached selector registry.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard or module_workflow_parity_suite_stays_aligned_with_published_fixture or module_workflow_direct_test_buckets_cover_selected_frontier'`
  - `bash -lc "! rg -n '^PUBLISHED_BOUNDED_WILDCARD_(RAW_MODULE_HELPER_CASES|COMPILE_CASES|PATTERN_CASES|PATTERN_MATCH_CASES|PATTERN_COLLECTION_CASES) = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the change limited to the bounded-wildcard published-case mirrors in `tests/python/test_module_workflow_parity_suite.py`. Do not widen into the module keyword/indexlike slices, the compiled-pattern module-helper slice, fixture-loader changes, or new shared support helpers in this run.
- Preserve the current published bounded-wildcard frontier exactly; the point is to delete one more owner-local mirror layer, not to reinterpret which bounded-wildcard rows are published.

## Notes
- `RBR-0895` is the next available architecture task id in the current checkout:
  - `RBR-0894` is already occupied by the ready feature task in `ops/tasks/ready/RBR-0894-catch-up-pattern-match-bytes-window-indexlike-boundary-pair.md`; and
  - `rg -n 'RBR-0895|RBR-0896|RBR-0897' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` found no tracked reservation or existing task for `RBR-0895`.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard or module_workflow_parity_suite_stays_aligned_with_published_fixture or module_workflow_direct_test_buckets_cover_selected_frontier'` currently passes (`47 passed, 1180 deselected`);
  - `rg -n '^PUBLISHED_BOUNDED_WILDCARD_(RAW_MODULE_HELPER_CASES|COMPILE_CASES|PATTERN_CASES|PATTERN_MATCH_CASES|PATTERN_COLLECTION_CASES) = ' tests/python/test_module_workflow_parity_suite.py` currently reports the five residual top-level mirrors at lines `231`, `344`, `348`, `352`, and `357`; and
  - those mirrors are bounded to one owner file and already feed the direct-bucket check plus the bounded-wildcard compile/pattern parametrizations, so the refactor stays small and local.
