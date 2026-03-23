# RBR-1017: Collapse compiled-pattern keyword-frontier case mirrors onto owner-path rows

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached case-id mirror stack from `tests/python/test_module_workflow_parity_suite.py` so the compiled-pattern keyword-frontier test derives its focused fixture/direct slices from the same canonical owner-path publication surface already used by the adjacent compiled-pattern publication contract instead of keeping a second local inventory of the same rows.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops open-coding the compiled-pattern keyword-frontier slice inside `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()`:
  - remove the detached `direct_cases_by_id` map built from `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES`; and
  - remove the hand-maintained `published_after_positional_count_case_ids`, `adjacent_published_case_ids`, `published_count_alias_case_ids`, and `published_fixture_case_ids` tuples.
- Replace that mirror stack with one file-local owner-path-derived route, or a strictly smaller equivalent, that selects the same three direct-case sub-slices and the same published fixture rows from the canonical compiled-pattern publication surface:
  - the two adjacent unexpected-keyword direct cases;
  - the two after-positional-count direct cases;
  - the two count-alias direct cases; and
  - the six published fixture rows that correspond to those direct cases on the compiled-pattern owner path.
- Keep the current keyword-frontier contract exact while shrinking the representation:
  - the published fixture rows still resolve in this order:
    - `workflow-module-sub-unexpected-keyword-str-compiled-pattern`
    - `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern`
    - `workflow-module-sub-count-alias-keyword-str-compiled-pattern`
    - `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`
    - `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern`
  - the focused direct cases still resolve in these grouped orders:
    - adjacent unexpected-keyword: `compiled-pattern-sub-unexpected-keyword-str`, `compiled-pattern-subn-unexpected-keyword-bytes`
    - after-positional-count: `compiled-pattern-sub-unexpected-keyword-after-positional-count-str`, `compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes`
    - count-alias: `compiled-pattern-sub-count-alias-keyword-str`, `compiled-pattern-subn-count-alias-keyword-bytes`
  - the explicit expected signature sets for the after-positional-count and count-alias groups remain unchanged; and
  - all three focused direct-case groups remain members of the published compiled-pattern signature set returned by `_assert_compiled_pattern_module_helper_publication_contract()`.
- Keep the cleanup structural and file-local:
  - prefer filtering `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS` and/or the data already returned by `_assert_compiled_pattern_module_helper_publication_contract()` over introducing another registry, side table, or mirror tuple;
  - keep `_assert_compiled_pattern_module_helper_publication_contract()` and `_compiled_pattern_module_helper_publication_signature(...)` as the canonical lower-level contract helpers unless a strictly smaller file-local successor preserves the same coverage;
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files; and
  - do not widen this run into raw-module owner paths, positional-indexlike publication, collection helper publication, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the remaining keyword-frontier mirror tuples over adding another detached helper layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- Completed 2026-03-23: replaced the keyword-frontier test’s detached `direct_cases_by_id` and case-id tuple mirrors in `tests/python/test_module_workflow_parity_suite.py` with an owner-path-derived filter over `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS`, keeping the same six published fixture rows plus the same adjacent, after-positional-count, and count-alias direct-case groups.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'` (`2 passed, 1449 deselected`).
- `RBR-1017` is the next available unreserved task id in the current checkout:
  - `python3` inspection over `ops/state/backlog.md`, `ops/state/current_status.md`, and all task queues reported `1017` as the first unused `RBR-` number in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is distinct from the earlier compiled-pattern owner-path tasks:
  - `RBR-0964` collapsed the larger compiled-pattern publication owner-path mirrors;
  - `RBR-0997` collapsed the compiled-pattern publication signature helper stack; and
  - `RBR-0999` centralized the shared compiled-pattern publication contract.
  - The remaining detached frontier-specific mirrors still live at the top of `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()` in the current checkout.
- The duplication target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `direct_cases_by_id` plus four hard-coded case-id tuples for this exact frontier at lines `4260` through `4275` in the current file; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'` currently passes (`2 passed, 1449 deselected`), so the acceptance slice is green before the cleanup.
