# RBR-0819: Add a grouped-replacement selector and collapse the suite sidecar

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Delete the grouped-replacement fixture path sidecar from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Keep that replacement parity suite anchored to one canonical correctness-harness selector instead of re-listing the same seven published fixture modules locally.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exports a dedicated selector for this grouped replacement slice:
  - add `GROUPED_REPLACEMENT_FIXTURE_SELECTOR = "grouped-replacement"`; and
  - register that selector in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` so `select_correctness_fixture_paths(GROUPED_REPLACEMENT_FIXTURE_SELECTOR)` returns this exact seven-file path order:
    - `collection_replacement_workflows.py`
    - `grouped_alternation_replacement_workflows.py`
    - `named_group_replacement_workflows.py`
    - `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
    - `nested_group_alternation_replacement_workflows.py`
    - `nested_group_replacement_workflows.py`
    - `quantified_nested_group_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines or references:
  - `GROUPED_REPLACEMENT_SELECTOR_FIXTURE_PATHS`; or
  - the `CORRECTNESS_FIXTURES_ROOT / "...replacement_workflows.py"` path tuple used only to rebuild that selector-owned slice.
- The grouped replacement surface in `tests/python/test_fixture_backed_replacement_parity_suite.py` loads through the new selector instead of the handwritten tuple:
  - import and use `GROUPED_REPLACEMENT_FIXTURE_SELECTOR` plus `select_correctness_fixture_paths(...)` from `rebar_harness.correctness`;
  - wire `ReplacementSurfaceSpec(id=GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID, ...)` to `select_correctness_fixture_paths(GROUPED_REPLACEMENT_FIXTURE_SELECTOR)` for `selector_fixture_paths`; and
  - do not add another local filename tuple, manifest-id keyed selector shim, or reordered path wrapper.
- Preserve the grouped replacement suite's existing manifest ownership and bundle-order behavior after the sidecar removal:
  - `GROUPED_REPLACEMENT_TEMPLATE_SURFACE.bundles` must still resolve, in order, to `collection-replacement-workflows`, `named-group-replacement-workflows`, `grouped-alternation-replacement-workflows`, `nested-group-replacement-workflows`, `nested-group-alternation-replacement-workflows`, `quantified-nested-group-replacement-workflows`, and `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows`;
  - keep `_grouped_replacement_template_bundles(...)`, `_grouped_replacement_contract_bundles(...)`, and the grouped-replacement contract assertions pinned to the same manifest ids they use today; and
  - do not broaden into fixture manifests under `tests/conformance/fixtures/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n 'GROUPED_REPLACEMENT_SELECTOR_FIXTURE_PATHS|CORRECTNESS_FIXTURES_ROOT / \"(collection_replacement_workflows|grouped_alternation_replacement_workflows|named_group_replacement_workflows|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows|nested_group_alternation_replacement_workflows|nested_group_replacement_workflows|quantified_nested_group_replacement_workflows)\\.py\"' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    GROUPED_REPLACEMENT_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_fixture_backed_replacement_parity_suite as mod

surface = mod.GROUPED_REPLACEMENT_TEMPLATE_SURFACE
assert surface.spec.selector_fixture_paths == select_correctness_fixture_paths(
    GROUPED_REPLACEMENT_FIXTURE_SELECTOR
)
assert tuple(path.name for path in surface.spec.selector_fixture_paths) == (
    "collection_replacement_workflows.py",
    "grouped_alternation_replacement_workflows.py",
    "named_group_replacement_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
    "nested_group_alternation_replacement_workflows.py",
    "nested_group_replacement_workflows.py",
    "quantified_nested_group_replacement_workflows.py",
)
assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `python/rebar_harness/correctness.py` and `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Prefer deleting the local grouped-replacement path mirror over adding another helper or another suite-local selector table.

## Notes
- `RBR-0819` is free in the current checkout:
  - `rg -n "RBR-0819|RBR-0820|RBR-0821|RBR-0822" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only a historical mention inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the current checkout is clean and the most recent cycle completed both architecture and feature work without inherited-dirty or post-task refresh churn.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1166 passed in 0.86s`);
  - `bash -lc "! rg -n 'GROUPED_REPLACEMENT_SELECTOR_FIXTURE_PATHS|CORRECTNESS_FIXTURES_ROOT / \"(collection_replacement_workflows|grouped_alternation_replacement_workflows|named_group_replacement_workflows|nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows|nested_group_alternation_replacement_workflows|nested_group_replacement_workflows|quantified_nested_group_replacement_workflows)\\.py\"' tests/python/test_fixture_backed_replacement_parity_suite.py"` currently fails exactly on the grouped replacement sidecar tuple; and
  - the selector probe in Acceptance currently fails only because `GROUPED_REPLACEMENT_FIXTURE_SELECTOR` does not exist yet (`ImportError: cannot import name 'GROUPED_REPLACEMENT_FIXTURE_SELECTOR' from 'rebar_harness.correctness'`), which is the exact cleanup this task is meant to land.
- The architectural shape is already established on the adjacent replacement surfaces:
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` already routes `CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR` and `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR` through `select_correctness_fixture_paths(...)`; and
  - this grouped slice is the remaining local path mirror in that module, so adding one canonical selector keeps the replacement harness on a single fixture-selection path instead of carrying a bespoke third style.

## Completion
- Added `GROUPED_REPLACEMENT_FIXTURE_SELECTOR = "grouped-replacement"` to `python/rebar_harness/correctness.py` and registered it in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` with the required seven-file grouped-replacement order.
- Removed the grouped-replacement suite-local path sidecar from `tests/python/test_fixture_backed_replacement_parity_suite.py` and wired `GROUPED_REPLACEMENT_TEMPLATE_SURFACE` directly to `select_correctness_fixture_paths(GROUPED_REPLACEMENT_FIXTURE_SELECTOR)` while preserving the existing manifest ownership and bundle reordering logic.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` (`1166 passed`), the required `rg` guard (no matches), and the selector/bundle-order probe from the acceptance criteria (`ok`).
