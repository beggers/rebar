# RBR-0877: Collapse remaining module-scope published-bundle rescans

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the remaining module-scope `published_fixture_bundle_by_manifest_id(...)` rescan chains from four parity-suite owners by routing those already-loaded bundle tuples through the existing `published_fixture_bundles_by_manifest_id(...)` helper, so the suites stop linearly rewalking the same bundle tuples every time they derive top-level manifest constants.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops deriving its top-level published bundle constants through repeated one-off lookups:
  - build one manifest-id map from `MODULE_WORKFLOW_SURFACE_BUNDLES` and derive `MODULE_WORKFLOW_BUNDLE` plus `MATCH_BEHAVIOR_BUNDLE` from that map;
  - build one manifest-id map from `PUBLIC_SURFACE_BUNDLES` and derive `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, and `PATTERN_OBJECT_BUNDLE` from that map;
  - keep the existing loaded bundle tuples, manifest ids, assertions, generated-spec ordering, and selected case ownership unchanged; and
  - do not widen the cleanup into deeper in-test lookup call sites that still need the one-off helper.
- `tests/python/test_branch_local_backreference_parity_suite.py` builds one manifest-id map from the existing `FIXTURE_BUNDLES` tuple and derives all current top-level manifest constants from that map instead of rescanning the tuple seven times:
  - keep `NAMED_BACKREFERENCE_BUNDLE`, `NUMBERED_BACKREFERENCE_BUNDLE`, `QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, and `NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE` bound to the same manifest ids they use today; and
  - preserve `FIXTURE_BUNDLES` load order, `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES`, generated parity specs, and direct-test case routing exactly.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` builds one manifest-id map from `FIXTURE_BUNDLES` and derives its five current top-level bundle constants from that map:
  - keep `NESTED_BROADER_RANGE_ALTERNATION_BUNDLE`, `NESTED_BROADER_RANGE_CONDITIONAL_BUNDLE`, `BROADER_RANGE_CONDITIONAL_BUNDLE`, `BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE`, and `NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE` pinned to the same manifest ids;
  - preserve `BACKTRACKING_TRACE_BUNDLES`, all supplemental case packs, and all suite-local ordering exactly; and
  - do not change the selected fixture path sets or the published-case frontier checks.
- `tests/python/test_conditional_group_exists_parity_suite.py` builds one manifest-id map from `FIXTURE_BUNDLES` and derives `QUANTIFIED_CONDITIONAL_BUNDLE` plus `QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE` from that map without changing the existing case inventory, sort-key logic, or generated parity specs.
- Keep this cleanup structural only:
  - use the existing `published_fixture_bundles_by_manifest_id(...)` helper in `tests/python/fixture_parity_support.py` rather than adding another selector helper, another suite-local registry, or another fixture-loader layer; and
  - do not change `python/rebar_harness/`, fixtures, reports, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_module_workflow_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Prefer deleting the repeated module-scope rescans over introducing another shared abstraction family.
- Keep the change limited to manifest-id indexing for already-loaded bundle tuples. Do not turn this into a broader parity-suite rewrite, a fixture discovery refactor, or a helper-contract change.

## Notes
- `RBR-0877` is the next available architecture task id in the current checkout:
  - `RBR-0876` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - no `RBR-0877` reservation appears in `ops/state/backlog.md`, `ops/state/current_status.md`, or the task queues; and
  - `ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run should target remaining harness duplication rather than blob deletion:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete and already isolated in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`1774 passed, 1 skipped in 1.73s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`1871 passed in 1.50s`); and
  - `bash -lc "! rg -n '^[A-Z0-9_]+ = published_fixture_bundle_by_manifest_id\\($' tests/python/test_module_workflow_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"` currently fails exactly on the remaining module-scope rescan chains in those four suites.
