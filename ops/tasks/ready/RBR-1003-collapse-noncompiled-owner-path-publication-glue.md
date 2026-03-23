## RBR-1003: Collapse noncompiled owner-path publication glue

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated noncompiled owner-path publication wrapper glue from `tests/python/test_module_workflow_parity_suite.py` so the five keyword/error/wrong-text-model publication tests run through one smaller file-local contract surface instead of each open-coding the same `_assert_owner_path_publication_contract(...)` plus `_assert_noncompiled_publication_direct_case_field_alignment(...)` sequence with only row sets, counts, and alignment flags changing.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for the repeated noncompiled owner-path publication contract, or a strictly smaller equivalent, that centralizes the current wrapper pattern shared by:
  - `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()`
- Repoint those five tests through that shared helper surface instead of leaving each test body to call `_assert_owner_path_publication_contract(...)` and then `_assert_noncompiled_publication_direct_case_field_alignment(...)` directly.
- Preserve the current publication contracts exactly while shrinking the glue:
  - the module keyword-helper slice still resolves to `14` published rows with `Counter({"str": 6, "bytes": 8})`, helper counts `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4})`, `keyword_arguments=True`, and `use_compiled_pattern=False`;
  - the module keyword-error slice still resolves to `13` published rows with `Counter({"str": 8, "bytes": 5})`, helper counts `Counter({"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4})`, `keyword_arguments=True`, `include_pattern_arg=True`, and `use_compiled_pattern=False`;
  - the pattern keyword-helper slice still resolves to `27` published rows with `Counter({"str": 15, "bytes": 12})`, helper counts `Counter({"search": 5, "match": 3, "fullmatch": 2, "findall": 3, "finditer": 3, "split": 3, "sub": 4, "subn": 4})`, and `keyword_arguments=True`;
  - the pattern keyword-error slice still resolves to `10` published rows with helper counts `Counter({"split": 2, "sub": 4, "subn": 4})` and `keyword_arguments=True`; and
  - the pattern wrong-text-model slice still resolves to `6` published rows with `Counter({"str": 4, "bytes": 2})`, helper counts `Counter({"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1})`, and `keyword_arguments=True`.
- Keep the cleanup structural and file-local:
  - keep `_assert_owner_path_publication_contract(...)` and `_assert_noncompiled_publication_direct_case_field_alignment(...)` as the canonical lower-level primitives unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this run into positional-indexlike publication helpers, compiled-pattern publication helpers, fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the repeated noncompiled owner-path wrapper glue over introducing another detached abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-1003` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1003|RBR-1004|RBR-1005|RBR-1006|RBR-1007' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty while the done queue currently ends at `RBR-1002-publish-pattern-replacement-bytes-no-match-count-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`5 passed, 1446 deselected`);
  - `tests/python/test_module_workflow_parity_suite.py` currently repeats the same owner-path-plus-field-alignment wrapper pattern in the five target tests at lines `4677`/`4695`, `4778`/`4795`, `4807`/`4827`, `4837`/`4851`, and `4861`/`4879`; and
  - the cleanup can stay structural and file-local because those tests differ only in the owner-path rows, expected counts, and alignment options they pass through the same two lower-level helpers.
