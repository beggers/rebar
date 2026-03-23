# RBR-0997: Collapse compiled-pattern publication signature helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the duplicated direct-vs-fixture compiled-pattern publication signature stack from `tests/python/test_module_workflow_parity_suite.py` so the compiled-pattern owner-path publication checks run through one canonical file-local signature surface, or a strictly smaller equivalent, instead of four narrowly split helpers.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer needs all four of these helpers as separate surfaces:
  - `_compiled_pattern_module_helper_direct_case_helper(...)`
  - `_compiled_pattern_module_helper_direct_case_args(...)`
  - `_compiled_pattern_module_helper_direct_signature(...)`
  - `_compiled_pattern_module_helper_fixture_signature(...)`
- Replace that quartet with one explicit shared compiled-pattern publication-signature helper, or a strictly smaller equivalent, that can build the same signature shape for both:
  - published `FixtureCase` rows selected from `MODULE_CALL_CASES` through `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS`; and
  - the direct compiled-pattern cases already routed through that owner path, including `CompiledPatternCompileCase`, `CompiledPatternModuleHelperCase`, `CompiledPatternModuleKeywordCallCase`, `CompiledPatternModuleKeywordErrorCase`, `CompiledPatternModuleHelperErrorCase`, and the bounded-wildcard direct cases already covered by the same owner-path rows.
- Preserve the current compiled-pattern publication signature semantics exactly while shrinking the helper surface:
  - helper names still align with the published fixture helper sequence, including compile rows mapping to `"compile"`;
  - compile rows still contribute empty direct-call args;
  - fixture rows still derive their pattern through `case_pattern(case)`;
  - flags still align through `case.flags` / `getattr(case, "flags", 0)`;
  - compiled-state alignment still runs through `case.use_compiled_pattern` / `getattr(case, "compiled", True)`;
  - keyword signatures still run through `_workflow_keyword_kwargs_signature(...)`; and
  - text-model alignment still distinguishes `str` and `bytes` from the underlying pattern payload.
- Repoint both compiled-pattern publication tests through the shared signature surface instead of building fixture signatures and direct-case signatures through separate helper families:
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`
  - `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()`
- Keep the cleanup structural and file-local:
  - keep `_assert_owner_path_publication_contract(...)` as the canonical owner-path count/order contract helper unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this run into the non-compiled publication helpers, collection helpers, fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the duplicated compiled-pattern signature machinery over introducing another detached helper layer.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0997` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-0997|RBR-0998|RBR-0999|RBR-1000|RBR-1001' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned only a historical mention inside `ops/tasks/done/RBR-0994-collapse-publication-direct-case-field-assertions.md` and no live task or state reservation for `RBR-0997`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'` currently passes (`2 passed, 1449 deselected`);
  - `tests/python/test_module_workflow_parity_suite.py` currently defines exactly one copy each of `_compiled_pattern_module_helper_direct_case_helper(...)`, `_compiled_pattern_module_helper_direct_case_args(...)`, `_compiled_pattern_module_helper_direct_signature(...)`, and `_compiled_pattern_module_helper_fixture_signature(...)`; and
  - the same file currently routes both compiled-pattern publication tests through that quartet, so this cleanup can delete duplicated signature-shape machinery without opening a new feature frontier.

## Completion Note
- Replaced the four compiled-pattern direct-vs-fixture publication signature helpers in `tests/python/test_module_workflow_parity_suite.py` with one shared `_compiled_pattern_module_helper_publication_signature(...)` helper and repointed both scoped owner-path publication tests through it.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'` (`2 passed, 1449 deselected`).
