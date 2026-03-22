# RBR-0899: Collapse the module-workflow compiled-pattern helper fixture mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the remaining published compiled-pattern module-helper fixture mirror in `tests/python/test_module_workflow_parity_suite.py`, so the owner file derives that published slice directly from the live compiled-pattern direct cases plus the fixture-backed `MODULE_CALL_CASES` inventory instead of keeping one extra top-level tuple constant.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`:
  - delete the mirrored top-level tuple instead of replacing it with another detached tuple/list/set/map; and
  - derive the same effective published fixture slice through one tiny file-local selector such as `_published_compiled_pattern_module_helper_fixture_cases()` built from the live owner data already present in the file.
- The published compiled-pattern selector stays tied to the existing direct owner path:
  - derive the fixture rows from `MODULE_CALL_CASES` plus the existing compiled-pattern direct-case inventory already used by `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`;
  - preserve the current published fixture ordering across the full 56-case slice; and
  - preserve the current `str` / `bytes` partition, helper counts, and direct-to-fixture signature alignment for that published subset.
- Route the current owner-path assertions through that live selector instead of the deleted mirror:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()`;
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`; and
  - any other reads of `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` in `tests/python/test_module_workflow_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change `MODULE_CALL_CASES`, compiled-pattern direct case inventories, fixture contents, selected case ids, parity expectations, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirror over adding a shared support module, another selector registry, or another owner-local sidecar table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_helper or module_workflow_parity_suite_stays_aligned_with_published_fixture or module_workflow_direct_test_buckets_cover_selected_frontier'`
  - `bash -lc "! rg -n '^PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the change limited to the residual compiled-pattern published-subset mirror in `tests/python/test_module_workflow_parity_suite.py`. Do not widen into module-keyword cleanup, compiled-pattern keyword-case cleanup, fixture-content edits, benchmark changes, or new shared helper modules in this run.
- Preserve the current published compiled-pattern module-helper frontier exactly; the point is to delete one more owner-local mirror layer, not to reinterpret which compiled-pattern rows stay published.

## Notes
- `RBR-0899` is the next available architecture task id in the current checkout:
  - `RBR-0898` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0898-publish-module-workflow-compiled-pattern-module-sub-subn-bool-count-complement-pair.md`; and
  - `rg -n 'RBR-0899|RBR-0900|RBR-0901' /home/ubuntu/rebar/ops/state/backlog.md /home/ubuntu/rebar/ops/state/current_status.md /home/ubuntu/rebar/ops/tasks -g '*.md'` found no tracked reservation or existing task for `RBR-0899`.
- There is no blocked architecture task to reopen or normalize first because `/home/ubuntu/rebar/ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_helper or module_workflow_parity_suite_stays_aligned_with_published_fixture or module_workflow_direct_test_buckets_cover_selected_frontier'` currently passes (`3 passed, 1234 deselected`);
  - `rg -n '^PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES = ' tests/python/test_module_workflow_parity_suite.py` currently reports the residual mirror at line `231`; and
  - the same owner file already derives the neighboring module-keyword, module-positional-indexlike, and pattern-keyword published slices from direct-case signatures, so this compiled-pattern mirror can be removed without introducing another abstraction layer.

## Completion
- Removed the `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` tuple mirror from `tests/python/test_module_workflow_parity_suite.py`.
- Added file-local compiled-pattern signature helpers plus `_published_compiled_pattern_module_helper_fixture_cases()` so the owner file now derives the published compiled-pattern fixture slice directly from `MODULE_CALL_CASES` and the live compiled-pattern direct inventories already used by the owner assertions.
- Rewired `test_module_workflow_direct_test_buckets_cover_selected_frontier()` and `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()` to use the live selector for ordering, `str` / `bytes` partition, helper-count, and fixture-to-direct alignment checks without changing the published 56-case frontier.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_helper or module_workflow_parity_suite_stays_aligned_with_published_fixture or module_workflow_direct_test_buckets_cover_selected_frontier'`
  - `bash -lc "! rg -n '^PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES = ' tests/python/test_module_workflow_parity_suite.py"`
