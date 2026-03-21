# RBR-0821: Add a collection-replacement selector and collapse singleton fixture loads

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Delete the remaining handwritten `collection_replacement_workflows.py` singleton fixture loads from the Python parity suites.
- Keep the collection/replacement owner manifest on one canonical correctness-harness selector so the callable-replacement and module-workflow suites stop re-stating the same path locally.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exports a dedicated selector for the collection/replacement owner manifest:
  - add `COLLECTION_REPLACEMENT_FIXTURE_SELECTOR = "collection-replacement"`; and
  - register that selector in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` so `select_correctness_fixture_paths(COLLECTION_REPLACEMENT_FIXTURE_SELECTOR)` returns exactly `("collection_replacement_workflows.py",)`.
- `tests/python/test_callable_replacement_parity_suite.py` no longer defines or references:
  - `COLLECTION_REPLACEMENT_FIXTURE_NAME`; or
  - a `CORRECTNESS_FIXTURES_ROOT / ...` singleton load for the collection owner bundle.
- `tests/python/test_callable_replacement_parity_suite.py` loads `COLLECTION_REPLACEMENT_OWNER_BUNDLE` through the new selector instead of the handwritten filename constant:
  - import and use `COLLECTION_REPLACEMENT_FIXTURE_SELECTOR` plus `select_correctness_fixture_paths(...)` from `rebar_harness.correctness`;
  - keep `COLLECTION_REPLACEMENT_OWNER_BUNDLE.manifest.manifest_id == "collection-replacement-workflows"`; and
  - keep `test_literal_callable_case_stays_aligned_with_published_collection_fixture()` proving that the owner bundle still matches the published manifest row order and still anchors `COLLECTION_REPLACEMENT_LITERAL_CALLABLE_CASE_ID`.
- `tests/python/test_module_workflow_parity_suite.py` no longer hard-codes `collection_replacement_workflows.py` when loading or asserting the collection owner bundle:
  - load `(COLLECTION_REPLACEMENT_BUNDLE,)` through `select_correctness_fixture_paths(COLLECTION_REPLACEMENT_FIXTURE_SELECTOR)`;
  - keep `test_literal_collection_suite_stays_aligned_with_published_fixture_rows()` anchored to the selector-owned path rather than a file-local `CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py"` literal; and
  - preserve the existing collection helper frontier split, selected case ids, and uncovered replacement rows without broadening the suite beyond its current owner-manifest partition.
- Do not broaden this cleanup into the module-workflow/match-behavior pair, the public-surface owner bundle tuple, callable manifest specs, fixture manifests under `tests/conformance/fixtures/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_FIXTURE_NAME|CORRECTNESS_FIXTURES_ROOT / \"collection_replacement_workflows\\.py\"' tests/python/test_callable_replacement_parity_suite.py tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    COLLECTION_REPLACEMENT_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_callable_replacement_parity_suite as callable_mod
import tests.python.test_module_workflow_parity_suite as workflow_mod

expected_paths = select_correctness_fixture_paths(
    COLLECTION_REPLACEMENT_FIXTURE_SELECTOR
)
assert tuple(path.name for path in expected_paths) == (
    "collection_replacement_workflows.py",
)
assert (
    callable_mod.COLLECTION_REPLACEMENT_OWNER_BUNDLE.manifest.path,
) == expected_paths
assert (workflow_mod.COLLECTION_REPLACEMENT_BUNDLE.manifest.path,) == expected_paths
assert callable_mod.COLLECTION_REPLACEMENT_OWNER_BUNDLE.manifest.manifest_id == (
    "collection-replacement-workflows"
)
assert workflow_mod.COLLECTION_REPLACEMENT_BUNDLE.manifest.manifest_id == (
    "collection-replacement-workflows"
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `python/rebar_harness/correctness.py`, `tests/python/test_callable_replacement_parity_suite.py`, and `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the duplicated singleton-path constants and direct `CORRECTNESS_FIXTURES_ROOT / ...` loads over adding another suite-local wrapper, manifest-id table, or helper module.

## Notes
- `RBR-0821` is free in the current checkout:
  - `rg -n "RBR-0821|RBR-0822|RBR-0823|RBR-0824|RBR-0825" ops/state/backlog.md ops/state/current_status.md ops/tasks` returned only a historical mention inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2747 passed in 2.11s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`804 passed, 1 skipped in 0.64s`);
  - `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_FIXTURE_NAME|CORRECTNESS_FIXTURES_ROOT / \"collection_replacement_workflows\\.py\"' tests/python/test_callable_replacement_parity_suite.py tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on the duplicated singleton fixture references in those two suites; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
try:
    from rebar_harness.correctness import COLLECTION_REPLACEMENT_FIXTURE_SELECTOR
    print(COLLECTION_REPLACEMENT_FIXTURE_SELECTOR)
except Exception as exc:
    print(type(exc).__name__, exc)
PY` currently fails with `ImportError` because that selector does not exist yet, which is the exact cleanup this task is meant to land.
- This cleanup follows the same selector-first simplification path as the recent fixture-sidecar removals:
  - `ops/tasks/done/RBR-0815-add-conditional-group-exists-selector-and-collapse-suite-sidecar.md`
  - `ops/tasks/done/RBR-0817-collapse-grouped-capture-fixture-sidecar-onto-owner-ordered-selector.md`
  - `ops/tasks/done/RBR-0819-add-grouped-replacement-selector-and-collapse-suite-sidecar.md`

## Completion
- Added `COLLECTION_REPLACEMENT_FIXTURE_SELECTOR = "collection-replacement"` to `python/rebar_harness/correctness.py`, registered it in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR`, and updated the shared selector expectation table in `tests/python/test_fixture_parity_support_contract.py` so the harness contract covers the new registry entry.
- Switched `tests/python/test_callable_replacement_parity_suite.py` and `tests/python/test_module_workflow_parity_suite.py` to load the collection owner manifest through `select_correctness_fixture_paths(COLLECTION_REPLACEMENT_FIXTURE_SELECTOR)` instead of suite-local `CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py"` loads, while preserving the existing manifest id and published row-order assertions.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` (`2747 passed`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`804 passed, 1 skipped`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`283 passed`), the required `rg` absence check (no matches), and the selector-path probe from Acceptance (`ok`).
