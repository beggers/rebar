# RBR-0897: Collapse the module-workflow pattern-keyword fixture mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the remaining published pattern-keyword fixture mirror in `tests/python/test_module_workflow_parity_suite.py`, so the owner file derives that published slice directly from the live pattern-keyword direct cases plus the fixture-backed `PATTERN_CASES` inventory instead of keeping one extra top-level tuple constant.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES`:
  - delete the mirrored top-level tuple instead of replacing it with another detached tuple/list/set/map; and
  - derive the same effective published fixture slice through one tiny file-local selector such as `_published_pattern_keyword_fixture_cases()` built from the live owner data already present in the file.
- The published pattern-keyword selector stays tied to the existing direct owner path:
  - derive the fixture rows from `PATTERN_KEYWORD_CALL_CASES` and `PATTERN_CASES` through the existing signature helpers or an equivalently direct file-local path;
  - preserve the current published fixture ordering across the full slice; and
  - preserve the current `str` / `bytes` partition and helper counts for the published pattern-keyword cases.
- Route the current owner-path assertions through that live selector instead of the deleted mirror:
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()`;
  - any adjacent count/order/text-model assertions in that test; and
  - any other reads of `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` in `tests/python/test_module_workflow_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change `PATTERN_KEYWORD_CALL_CASES`, `PATTERN_CASES`, fixture contents, selected case ids, parity expectations, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirror over adding a shared support module, another selector registry, or another owner-local sidecar table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword or module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_parity_suite_stays_aligned_with_published_fixture'`
  - `bash -lc "! rg -n '^PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the change limited to the residual pattern-keyword fixture mirror in `tests/python/test_module_workflow_parity_suite.py`. Do not widen into compiled-pattern helper cleanup, collection/replacement cleanup, fixture-content edits, benchmark changes, or new shared helper modules in this run.
- Preserve the current published pattern-keyword frontier exactly; the point is to delete one more owner-local mirror layer, not to reinterpret which pattern-keyword rows stay published.

## Notes
- `RBR-0897` is the next available architecture task id in the current checkout:
  - `RBR-0896` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0896-publish-module-workflow-module-sub-subn-bool-count-complement-pair.md`; and
  - `rg -n 'RBR-0897|RBR-0898|RBR-0899' /home/ubuntu/rebar/ops/state/backlog.md /home/ubuntu/rebar/ops/state/current_status.md /home/ubuntu/rebar/ops/tasks -g '*.md'` found no tracked reservation or existing task for `RBR-0897`.
- There is no blocked architecture task to reopen or normalize first because `/home/ubuntu/rebar/ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword or module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_parity_suite_stays_aligned_with_published_fixture'` currently passes (`53 passed, 1179 deselected`);
  - `rg -n '^PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES = ' tests/python/test_module_workflow_parity_suite.py` currently reports the residual mirror at line `231`; and
  - the same owner file already derives the neighboring module-keyword and positional-indexlike published slices from direct-case signatures, so this pattern-keyword mirror can be removed without introducing another abstraction layer.

## Completion
- Removed the `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` tuple mirror from `tests/python/test_module_workflow_parity_suite.py`.
- Added a file-local pattern-keyword signature path plus `_published_pattern_keyword_fixture_cases()` so the owner file now derives the published pattern-keyword fixture slice directly from `PATTERN_KEYWORD_CALL_CASES` and `PATTERN_CASES`.
- Rewired `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()` to use the live selector for its ordering, `str` / `bytes` partition, helper-count, and fixture-to-direct alignment checks without changing the published frontier.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword or module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_parity_suite_stays_aligned_with_published_fixture'`
  - `bash -lc "! rg -n '^PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES = ' tests/python/test_module_workflow_parity_suite.py"`
