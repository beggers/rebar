## RBR-1005: Collapse positional-indexlike publication wrapper glue

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining positional-indexlike publication wrapper glue from `tests/python/test_module_workflow_parity_suite.py` so the two positional-indexlike publication tests run through one smaller file-local contract surface instead of each open-coding the same `_assert_positional_indexlike_publication_contract(...)` plus `_assert_noncompiled_publication_direct_case_field_alignment(...)` sequence with only slice-specific expectations changing.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for the repeated positional-indexlike publication wrapper, or a strictly smaller equivalent, that centralizes the current composition shared by:
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases()`
- Repoint both tests through that shared helper surface instead of leaving each body to:
  - call `_assert_positional_indexlike_publication_contract(...)`; and then
  - separately call `_assert_noncompiled_publication_direct_case_field_alignment(...)`.
- Preserve the current positional-indexlike publication contracts exactly while shrinking the glue:
  - the module positional-indexlike slice still resolves to `3` published fixture rows and `3` selected direct rows, with `Counter({"split": 1, "sub": 1, "subn": 1})`;
  - the module `str` fixture split still stays `("workflow-module-sub-count-indexlike-positional-str",)`;
  - the module `bytes` fixture split still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module published fixture order still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-sub-count-indexlike-positional-str", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module selected direct-case order still stays `("module-split-maxsplit-indexlike-positional-bytes", "module-sub-count-indexlike-positional-str", "module-subn-count-indexlike-positional-bytes")`;
  - the module slice still verifies `keyword_arguments=False`, `include_pattern_arg=True`, and `use_compiled_pattern=False` through the shared wrapper;
  - the pattern positional-indexlike slice still resolves to `9` published fixture rows and `9` selected direct rows, with `Counter({"search": 2, "match": 1, "fullmatch": 1, "findall": 1, "finditer": 1, "split": 1, "sub": 1, "subn": 1})`;
  - the pattern `str` fixture split still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-subn-count-indexlike-positional-str")`;
  - the pattern `bytes` fixture split still stays `("workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes")`;
  - the pattern published fixture order still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes", "workflow-pattern-subn-count-indexlike-positional-str")`;
  - the pattern selected direct-case order still stays `("pattern-search-pos-indexlike-positional-str", "pattern-search-endpos-indexlike-positional-bytes", "pattern-match-window-indexlike-positional-bytes", "pattern-fullmatch-window-indexlike-positional-bytes", "pattern-findall-window-indexlike-positional-str", "pattern-finditer-window-indexlike-positional-bytes", "pattern-split-maxsplit-indexlike-positional-str", "pattern-sub-count-indexlike-positional-bytes", "pattern-subn-count-indexlike-positional-str")`; and
  - the pattern slice still preserves the `include_fixture_case=lambda case: case.kwargs == {}` filter and `keyword_arguments=False` alignment checks through the shared wrapper.
- Keep the cleanup structural and file-local:
  - keep `_assert_positional_indexlike_publication_contract(...)` and `_assert_noncompiled_publication_direct_case_field_alignment(...)` as the canonical lower-level primitives unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this run into owner-path publication helpers, compiled-pattern publication helpers, direct-case inventory assertions, fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the repeated positional-indexlike wrapper glue over introducing another detached abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-1005` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1005|RBR-1006|RBR-1007|RBR-1008' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only inside prior done-task notes, with no live reservation in ready, in-progress, blocked, or done task filenames; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-1004-catch-up-pattern-replacement-bytes-no-match-count-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`2 passed, 1449 deselected`);
  - `tests/python/test_module_workflow_parity_suite.py` still repeats the same wrapper shape in the two target tests at the current `published_fixture_cases, selected_direct_cases = (...)` assignments around lines `4758` and `5018`, followed by `_assert_noncompiled_publication_direct_case_field_alignment(...)` calls at lines `4787` and `5073`; and
  - the cleanup can stay structural and file-local because the two tests differ only in the positional-indexlike expectations they pass through the same two lower-level helpers.
