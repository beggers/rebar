# RBR-1015: Collapse positional-indexlike publication selector onto owner-path rows

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the positional-indexlike publication side path from `tests/python/test_module_workflow_parity_suite.py` so the module and pattern positional-indexlike publication slices use the same explicit owner-path routing machinery as the adjacent bounded-wildcard, keyword, keyword-error, and compiled-pattern publication tests instead of maintaining a separate signature-matching selector stack.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` replaces the current positional-indexlike signature-matching helper stack with one owner-path-based publication surface, or a strictly smaller equivalent, for both positional-indexlike slices:
  - the module slice currently routed through `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`; and
  - the pattern slice currently routed through `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`.
- Repoint all current positional-indexlike consumers through that owner-path surface instead of leaving them on `_published_positional_indexlike_fixture_cases(...)`, `_selected_positional_indexlike_direct_cases(...)`, and `_assert_positional_indexlike_publication_contract(...)`:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()`
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases()`
- Delete the bespoke positional-indexlike signature-routing machinery if the owner-path route leaves it unused, or reduce it to a strictly smaller equivalent:
  - `_positional_indexlike_direct_case_pattern_and_args(...)`
  - `_positional_indexlike_direct_signature(...)`
  - `_workflow_positional_indexlike_fixture_signature(...)`
  - `_published_positional_indexlike_fixture_cases(...)`
  - `_selected_positional_indexlike_direct_cases(...)`
  - `_assert_positional_indexlike_publication_contract(...)`
- Preserve the exact module positional-indexlike publication contract while moving it onto owner-path rows:
  - the published fixture-case order still resolves to:
    - `workflow-module-split-maxsplit-indexlike-positional-bytes`
    - `workflow-module-sub-count-indexlike-positional-str`
    - `workflow-module-subn-count-indexlike-positional-bytes`
  - the direct-case order still resolves to:
    - `module-split-maxsplit-indexlike-positional-bytes`
    - `module-sub-count-indexlike-positional-str`
    - `module-subn-count-indexlike-positional-bytes`
  - helper counts still resolve to `Counter({"split": 1, "sub": 1, "subn": 1})`;
  - the `str`/`bytes` split still resolves to one `str` row and two `bytes` rows;
  - the fixture rows still keep `include_pattern_arg is True`, `use_compiled_pattern is False`, `kwargs == {}`, and positional-argument signatures aligned through `_workflow_positional_args_signature(...)`; and
  - the direct-test bucket coverage test still publishes those same three fixture case ids on the shared `module-positional-indexlike-helper` bucket.
- Preserve the exact pattern positional-indexlike publication contract while moving it onto owner-path rows:
  - the published fixture-case order still resolves to:
    - `workflow-pattern-search-str-pos-indexlike-positional`
    - `workflow-pattern-search-bytes-endpos-indexlike-positional`
    - `workflow-pattern-match-bytes-window-indexlike-positional`
    - `workflow-pattern-fullmatch-bytes-window-indexlike-positional`
    - `workflow-pattern-findall-str-window-indexlike-positional`
    - `workflow-pattern-finditer-bytes-window-indexlike-positional`
    - `workflow-pattern-split-str-maxsplit-indexlike-positional`
    - `workflow-pattern-sub-count-indexlike-positional-bytes`
    - `workflow-pattern-subn-count-indexlike-positional-str`
  - the direct-case order still resolves to:
    - `pattern-search-pos-indexlike-positional-str`
    - `pattern-search-endpos-indexlike-positional-bytes`
    - `pattern-match-window-indexlike-positional-bytes`
    - `pattern-fullmatch-window-indexlike-positional-bytes`
    - `pattern-findall-window-indexlike-positional-str`
    - `pattern-finditer-window-indexlike-positional-bytes`
    - `pattern-split-maxsplit-indexlike-positional-str`
    - `pattern-sub-count-indexlike-positional-bytes`
    - `pattern-subn-count-indexlike-positional-str`
  - helper counts still resolve to `Counter({"search": 2, "match": 1, "fullmatch": 1, "findall": 1, "finditer": 1, "split": 1, "sub": 1, "subn": 1})`;
  - the `str`/`bytes` split still resolves to four `str` rows and five `bytes` rows;
  - the fixture rows still keep `kwargs == {}` and positional-argument signatures aligned through `_workflow_positional_args_signature(...)`; and
  - the pattern positional-indexlike publication test still proves those same nine fixture/direct pairs without reopening a second selector path outside the owner-row machinery.
- Keep the cleanup structural and file-local:
  - prefer explicit file-local owner-path rows over another detached selector/signature abstraction;
  - keep `_assert_owner_path_publication_contract(...)` and `_assert_noncompiled_owner_path_publication_contract(...)` as the canonical publication-contract helpers unless a strictly smaller file-local successor preserves the same coverage;
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files in this run; and
  - do not widen this task into CPython behavior coverage, positional-indexlike coercion behavior, bounded-wildcard publication, keyword publication, or compiled-pattern helper behavior beyond the owner-path routing cleanup above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the positional-indexlike signature-matching selector path over introducing another helper layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or README/current-status/backlog prose in this run.

## Notes
- Completed 2026-03-23: collapsed the positional-indexlike publication side path in `tests/python/test_module_workflow_parity_suite.py` onto explicit module and pattern owner-path rows, repointed the direct-test bucket plus both publication tests through `_published_owner_path_fixture_cases(...)` / `_assert_noncompiled_owner_path_publication_contract(...)`, and deleted the old signature-matching selector helpers.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'` (`3 passed, 1448 deselected`).
- `RBR-1015` is the next available unreserved task id in the current checkout:
  - `python3` inspection over `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues reported `next_free 1015`, with `RBR-1013` and `RBR-1014` already occupied and no reservation for `RBR-1015`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines a positional-indexlike signature-routing stack centered on `_published_positional_indexlike_fixture_cases(...)`, `_selected_positional_indexlike_direct_cases(...)`, and `_assert_positional_indexlike_publication_contract(...)`;
  - the direct-test bucket coverage test still routes `module-positional-indexlike-helper` through that side path instead of the owner-path machinery already used by the adjacent publication buckets; and
  - live pairing probes show the current positional-indexlike publication route is already a fixed explicit mapping, making owner-path rows a smaller representation:
    - module: `workflow-module-split-maxsplit-indexlike-positional-bytes -> module-split-maxsplit-indexlike-positional-bytes`, `workflow-module-sub-count-indexlike-positional-str -> module-sub-count-indexlike-positional-str`, `workflow-module-subn-count-indexlike-positional-bytes -> module-subn-count-indexlike-positional-bytes`
    - pattern: `workflow-pattern-search-str-pos-indexlike-positional -> pattern-search-pos-indexlike-positional-str`, `workflow-pattern-search-bytes-endpos-indexlike-positional -> pattern-search-endpos-indexlike-positional-bytes`, `workflow-pattern-match-bytes-window-indexlike-positional -> pattern-match-window-indexlike-positional-bytes`, `workflow-pattern-fullmatch-bytes-window-indexlike-positional -> pattern-fullmatch-window-indexlike-positional-bytes`, `workflow-pattern-findall-str-window-indexlike-positional -> pattern-findall-window-indexlike-positional-str`, `workflow-pattern-finditer-bytes-window-indexlike-positional -> pattern-finditer-window-indexlike-positional-bytes`, `workflow-pattern-split-str-maxsplit-indexlike-positional -> pattern-split-maxsplit-indexlike-positional-str`, `workflow-pattern-sub-count-indexlike-positional-bytes -> pattern-sub-count-indexlike-positional-bytes`, `workflow-pattern-subn-count-indexlike-positional-str -> pattern-subn-count-indexlike-positional-str`
- The verification slice is green before the cleanup:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'` currently passes with `3 passed, 1448 deselected`.
