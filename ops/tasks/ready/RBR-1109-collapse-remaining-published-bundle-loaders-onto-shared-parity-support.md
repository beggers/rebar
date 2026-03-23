# RBR-1109: Collapse remaining published bundle loaders onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining top-level published fixture-bundle loading/indexing boilerplate that still lives in three Python parity owners even though `tests/python/fixture_parity_support.py` already exposes `load_published_fixture_bundles(...)` for that exact selector-to-bundle-to-manifest-index flow.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` stops open-coding the two-step top-level parser-owner load path:
  - `OWNER_FIXTURE_BUNDLES = tuple(build_selected_fixture_bundle(path) for path in select_correctness_fixture_paths(...))`; and
  - `OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id(OWNER_FIXTURE_BUNDLES)`.
- `tests/python/test_module_workflow_parity_suite.py` routes both owner-local full-manifest bundle loads through `load_published_fixture_bundles(...)` instead of repeating the same tuple-build plus manifest-id-index boilerplate:
  - the `MODULE_WORKFLOW_SURFACE_*` bundle load for `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR`; and
  - the `PUBLIC_SURFACE_*` bundle load for `PUBLIC_SURFACE_FIXTURE_SELECTOR`, while preserving the current `_public_surface_case_contract_token` pattern extraction.
- `tests/python/test_callable_replacement_parity_suite.py` stops open-coding the same top-level callable-fixture load/index sequence for `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`; `CALLABLE_FIXTURE_PATHS` may remain only where the file still needs the raw ordered paths for assertions or task-local probes.
- Preserve current owner behavior after the cleanup:
  - the returned bundle order still matches the selector order each file currently expects;
  - existing manifest-id aliases such as `PARSER_MATRIX_OWNER_BUNDLE`, `MODULE_WORKFLOW_BUNDLE`, `PUBLIC_API_BUNDLE`, and the callable `FIXTURE_BUNDLES_BY_MANIFEST_ID` entries continue resolving to the same published manifests; and
  - suite expectations, selected-case slices, and direct parity assertions remain unchanged.
- Keep the cleanup structural and limited to the three owner files above. Do not widen it into `tests/python/fixture_parity_support.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, harness implementation code, reports, README text, or tracked state prose unless a tiny import-only support tweak is strictly necessary to use the existing helper.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
- `bash -lc "! rg -n '^OWNER_FIXTURE_BUNDLES = tuple\\(|^OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(|^MODULE_WORKFLOW_SURFACE_BUNDLES = tuple\\(|^MODULE_WORKFLOW_SURFACE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(|^PUBLIC_SURFACE_BUNDLES = tuple\\(|^PUBLIC_SURFACE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(|^FIXTURE_BUNDLES = tuple\\(|^FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(' tests/python/test_parser_matrix_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Prefer reusing `load_published_fixture_bundles(...)` exactly as it exists today over adding another wrapper, registry, or owner-specific helper layer.
- Preserve the current selector-owned ordering and manifest-id validation semantics from `published_fixture_bundles_by_manifest_id(...)`.
- Do not broaden this into the deeper `_load_surface(...)` refactor path in `tests/python/test_fixture_backed_replacement_parity_suite.py`; that surface still mixes selective bundle rebuilding and manifest reshaping that is out of scope for this task.

## Notes
- `RBR-1109` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1108`; and
  - `rg -n 'RBR-1109|RBR-1110|RBR-1111|RBR-1112|RBR-1113' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_parser_matrix_parity_suite.py:35-39` still open-codes the parser-owner bundle tuple plus manifest-id index;
  - `tests/python/test_module_workflow_parity_suite.py:174-181` still open-codes the module-workflow surface bundle tuple plus manifest-id index;
  - `tests/python/test_module_workflow_parity_suite.py:415-422` still open-codes the public-surface bundle tuple plus manifest-id index; and
  - `tests/python/test_callable_replacement_parity_suite.py:1153-1156` still open-codes the callable-replacement bundle tuple plus manifest-id index.
- The focused parity slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` returned `4696 passed, 29 skipped` in this run.
- The negative `rg` verification currently fails exactly on the targeted owner-local boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.
