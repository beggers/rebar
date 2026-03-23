# RBR-1031: Collapse module-workflow owner-path row wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the seven bespoke owner-path row wrapper dataclasses from `tests/python/test_module_workflow_parity_suite.py` so the module-workflow owner-path publication checks read from one canonical same-file row shape instead of repeating the same `fixture_case_id`/`direct_case` boilerplate with only minor `text_model` variations.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines these detached owner-path row wrapper classes:
  - `CompiledPatternModuleHelperOwnerPathRow`
  - `ModuleKeywordOwnerPathRow`
  - `ModulePositionalIndexLikeOwnerPathRow`
  - `PatternKeywordPublicationOwnerPathRow`
  - `BoundedWildcardModuleOwnerPathRow`
  - `PatternTypeErrorOwnerPathRow`
  - `PatternPositionalIndexLikeOwnerPathRow`
- Replace those wrappers with one canonical same-file owner-path row representation, or an equivalently smaller same-file structure, that still keeps `fixture_case_id`, `direct_case`, and `text_model` available to the existing owner-path helpers without adding a new support module or detached registry.
- Keep these owner-path row tables on the same file and derive their `text_model` partitioning from the canonical row representation instead of bespoke wrapper classes:
  - `BOUNDED_WILDCARD_RAW_MODULE_HELPER_OWNER_PATH_ROWS`
  - `_PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS`
  - `_PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS`
  - `MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`
  - `MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS`
  - `MODULE_POSITIONAL_INDEXLIKE_PUBLICATION_OWNER_PATH_ROWS`
  - `PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS`
  - `PATTERN_POSITIONAL_INDEXLIKE_PUBLICATION_OWNER_PATH_ROWS`
  - `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS`
- Keep `_owner_path_fixture_case_ids(...)`, `_assert_owner_path_publication_contract(...)`, and `_assert_noncompiled_owner_path_publication_contract(...)` on the same route while preserving the exact ordered `str`/`bytes` fixture-case partitions they currently assert for those row tables.
- Preserve the current owner-path pairings, helper counts, and fixture ordering for the bounded wildcard, keyword, positional-indexlike, pattern-type-error, and compiled-pattern module-helper publication lanes; this cleanup should only remove wrapper duplication, not change which fixture cases map to which direct cases.
- Keep the existing owner-path verification slice green without widening scope into fixtures, harness code, reports, or implementation behavior.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'owner_path_publication_contract or owner_path_case_ids_stay_in_fixture_order or bounded_wildcard or type_error_owner_path or module_keyword or positional_indexlike or pattern_keyword or compiled_pattern_module_helper'`
- `bash -lc "! rg -n 'class (CompiledPatternModuleHelperOwnerPathRow|ModuleKeywordOwnerPathRow|ModulePositionalIndexLikeOwnerPathRow|PatternKeywordPublicationOwnerPathRow|BoundedWildcardModuleOwnerPathRow|PatternTypeErrorOwnerPathRow|PatternPositionalIndexLikeOwnerPathRow)' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the duplicated wrapper dataclasses over adding another abstraction layer, helper module, or registry.
- Do not edit correctness fixtures, benchmark workloads, reports, README/current-status/backlog prose, or the Rust/Python implementation.

## Notes
- `RBR-1031` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-103[1-9]|RBR-104[0-9]|RBR-105[0-9]" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ls -1 ops/tasks/done | tail -n 40` shows `RBR-1030` as the newest landed task.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue no-op rule does not trigger in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime dashboard shows no inherited-dirty checkpoint churn, stalled post-task refresh path, or other active queue bottleneck.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` currently defines seven near-identical owner-path row wrappers that differ only in how they derive `text_model`; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'owner_path_publication_contract or owner_path_case_ids_stay_in_fixture_order or bounded_wildcard or type_error_owner_path or module_keyword or positional_indexlike or pattern_keyword or compiled_pattern_module_helper'` currently passes (`415 passed, 1036 deselected`).
