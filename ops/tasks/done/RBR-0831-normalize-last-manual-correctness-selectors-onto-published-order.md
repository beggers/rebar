# RBR-0831: Normalize the last manual correctness selectors onto published order

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the last three correctness selector rows in `python/rebar_harness/correctness.py` that still carry a suite-local tuple order instead of deriving their subset directly from the canonical `published-full-suite` selector.
- Collapse the remaining order-sensitive test assumptions in the affected parity suites so the correctness harness has one selector-order rule instead of a helper-backed rule plus three manual exceptions.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` stops hand-maintaining local tuple order for the last three manual selector rows:
  - replace the current manual filename tuples for `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR`, `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR`, and `GROUPED_CAPTURE_FIXTURE_SELECTOR` with `_published_fixture_subset(...)`;
  - keep `PUBLIC_SURFACE_FIXTURE_SELECTOR` and `PARSER_PARITY_FIXTURE_SELECTOR` unchanged unless a minimal refactor is needed to keep the selector table legible; and
  - do not add another selector helper, another registry, or another mirror table.
- `tests/python/test_fixture_parity_support_contract.py` collapses the split selector-order contract onto one invariant for every declared nondefault correctness selector:
  - tighten `test_shared_correctness_fixture_selectors_resolve_published_paths()` so it asserts `select_correctness_fixture_paths(selector)` is the exact published-full-suite ordered subset for that selector, not merely the same set of paths;
  - delete `_helper_backed_published_order_selectors()` and the extra helper-backed-only order test once the global invariant covers every selector; and
  - keep the remaining declared-selector, unknown-selector, and tracked-inventory checks in the same file.
- `tests/python/test_module_workflow_parity_suite.py` no longer depends on the selector tuple order for the `module-workflow-surface` bundle pair:
  - stop unpacking or indexing `MODULE_WORKFLOW_SURFACE_FIXTURE_PATHS` as the source of truth for `MODULE_WORKFLOW_BUNDLE` versus `MATCH_BEHAVIOR_BUNDLE`;
  - resolve those two bundles by manifest id (`module-workflow-surface` and `match-behavior-smoke`) after loading the published selector paths; and
  - use each bundle's own `manifest.path` for the fixture-path assertions instead of `MODULE_WORKFLOW_SURFACE_FIXTURE_PATHS[0]` / `[1]`.
- `tests/python/test_grouped_capture_parity_suite.py` keeps the grouped-capture owner-order assertion anchored to the canonical published selector subset rather than the superseded local tuple:
  - update `test_fixture_bundles_load_expected_published_owner_order()` so it checks the bundle order against the published `grouped-capture` subset order after selector normalization; and
  - keep the suite's bundle membership, manifest ids, and selected case ids unchanged.
- `tests/python/test_conditional_group_exists_parity_suite.py` stops slicing `FIXTURE_BUNDLES` by tuple position:
  - replace `FIXTURE_BUNDLES[:6]`, `FIXTURE_BUNDLES[6:12]`, and `FIXTURE_BUNDLES[12:]` with manifest-id-based partitions that preserve the current logical grouping;
  - keep the current three families intact:
    - base: `optional-group-conditional-workflows`, `conditional-group-exists-workflows`, `conditional-group-exists-no-else-workflows`, `conditional-group-exists-empty-else-workflows`, `conditional-group-exists-empty-yes-else-workflows`, `conditional-group-exists-fully-empty-workflows`;
    - quantified: `conditional-group-exists-quantified-workflows`, `conditional-group-exists-quantified-alternation-workflows`, `conditional-group-exists-no-else-quantified-workflows`, `conditional-group-exists-empty-else-quantified-workflows`, `conditional-group-exists-empty-yes-else-quantified-workflows`, `conditional-group-exists-fully-empty-quantified-workflows`;
    - nested-or-alternation: `conditional-group-exists-nested-workflows`, `conditional-group-exists-no-else-nested-workflows`, `conditional-group-exists-empty-else-nested-workflows`, `conditional-group-exists-empty-yes-else-nested-workflows`, `conditional-group-exists-fully-empty-nested-workflows`, `conditional-group-exists-alternation-workflows`, `conditional-group-exists-no-else-alternation-workflows`, `conditional-group-exists-empty-else-alternation-workflows`, `conditional-group-exists-empty-yes-else-alternation-workflows`, `conditional-group-exists-fully-empty-alternation-workflows`; and
  - keep the generated quantified conditional anchors and the selected frontier unchanged in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '_helper_backed_published_order_selectors\\(|MODULE_WORKFLOW_SURFACE_FIXTURE_PATHS\\[[01]\\]|FIXTURE_BUNDLES\\[:6\\]|FIXTURE_BUNDLES\\[6:12\\]|FIXTURE_BUNDLES\\[12:\\]' tests/python/test_fixture_parity_support_contract.py tests/python/test_module_workflow_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR,
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
    MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR,
)

selectors = (
    CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR,
    MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR,
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
)
published = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
]
for selector in selectors:
    actual = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector]
    expected = tuple(name for name in published if name in set(actual))
    assert actual == expected, f"{selector}: {actual!r} != {expected!r}"
print("ok")
PY`

## Constraints
- Keep this cleanup structural. Do not edit fixture manifests under `tests/conformance/fixtures/`, reports, README copy, benchmark files, or tracked project-state prose.
- Prefer deleting local order assumptions over adding another helper layer or another expectation table.
- Do not broaden the selector scope, selected case ids, or parity frontier; this task is about converging the harness on one published-order rule.

## Notes
- `RBR-0831` is free in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only `RBR-0830` on the current frontier in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0831|^RBR-0832|^RBR-0833'` returned no conflicting task files in this run.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed architecture, architecture-implementation, feature work, cleanup, and reporting cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is live in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_bundle_contract_covers_regression_compile_cases tests/python/test_module_workflow_parity_suite.py::test_match_behavior_parity_suite_stays_aligned_with_published_fixture tests/python/test_grouped_capture_parity_suite.py::test_fixture_bundles_load_expected_published_owner_order tests/python/test_conditional_group_exists_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests` currently passes (`27 passed in 0.15s`);
  - the selector-order probe in Acceptance currently fails exactly on the remaining manual rows, starting with `conditional-group-exists`; and
  - `PYTHONPATH=python python3 - <<'PY' ... PY` over `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` reports only three remaining nondefault selector mismatches against canonical published order: `conditional-group-exists`, `module-workflow-surface`, and `grouped-capture`.
- This task is the direct follow-up left in `ops/tasks/done/RBR-0829-collapse-helper-backed-correctness-selector-ordering-onto-published-subsets.md`: helper-backed selectors are normalized now, and these three manual rows are the remaining exceptions if the harness wants one global correctness-selector ordering rule.

## Completion
- 2026-03-21: Replaced the remaining manual selector rows for `conditional-group-exists`, `module-workflow-surface`, and `grouped-capture` with `_published_fixture_subset(...)` in `python/rebar_harness/correctness.py`, leaving `public-surface` and `parser-parity` unchanged.
- 2026-03-21: Collapsed `tests/python/test_fixture_parity_support_contract.py` onto one global ordered-subset invariant for every declared nondefault correctness selector and deleted the helper-backed-only selector-order helper/test.
- 2026-03-21: Refreshed the order-sensitive suites so they no longer depend on superseded local tuple positions:
  - `tests/python/test_module_workflow_parity_suite.py` now resolves the `module-workflow-surface` and `match-behavior-smoke` bundles by manifest id after loading the selector paths.
  - `tests/python/test_grouped_capture_parity_suite.py` now anchors bundle order to the published `grouped-capture` selector subset.
  - `tests/python/test_conditional_group_exists_parity_suite.py` now builds its base, quantified, and nested-or-alternation families from explicit manifest-id partitions instead of slicing `FIXTURE_BUNDLES` by index.
- 2026-03-21: Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '_helper_backed_published_order_selectors\\(|MODULE_WORKFLOW_SURFACE_FIXTURE_PATHS\\[[01]\\]|FIXTURE_BUNDLES\\[:6\\]|FIXTURE_BUNDLES\\[6:12\\]|FIXTURE_BUNDLES\\[12:\\]' tests/python/test_fixture_parity_support_contract.py tests/python/test_module_workflow_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`
  - the selector-order probe from the acceptance block (`ok`)
