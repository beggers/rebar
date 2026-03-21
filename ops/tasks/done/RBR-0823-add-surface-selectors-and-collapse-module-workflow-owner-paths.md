# RBR-0823: Add surface selectors and collapse module-workflow owner path mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Delete the remaining raw owner-manifest path mirrors in `tests/python/test_module_workflow_parity_suite.py`.
- Keep the module-workflow/match-behavior pair and the public-surface trio anchored to the shared correctness-harness selector registry instead of re-listing those published fixture files locally.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exports two dedicated selectors for the remaining surface-owner slices:
  - add `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR = "module-workflow-surface"`; and
  - add `PUBLIC_SURFACE_FIXTURE_SELECTOR = "public-surface"`.
- Register those selectors in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` with the exact owner orders already baked into `tests/python/test_module_workflow_parity_suite.py` today:
  - `select_correctness_fixture_paths(MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR)` returns:
    - `module_workflow_surface.py`
    - `match_behavior_smoke.py`
  - `select_correctness_fixture_paths(PUBLIC_SURFACE_FIXTURE_SELECTOR)` returns:
    - `public_api_surface.py`
    - `exported_symbol_surface.py`
    - `pattern_object_surface.py`
- `tests/python/test_module_workflow_parity_suite.py` loads both owner slices through those selectors instead of raw `CORRECTNESS_FIXTURES_ROOT / ...` literals:
  - import and use `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR`, `PUBLIC_SURFACE_FIXTURE_SELECTOR`, and `select_correctness_fixture_paths(...)` from `rebar_harness.correctness`;
  - wire `(MODULE_WORKFLOW_BUNDLE, MATCH_BEHAVIOR_BUNDLE)` to the selector-owned module-workflow path tuple; and
  - wire `PUBLIC_SURFACE_BUNDLES` to the selector-owned public-surface path tuple.
- Preserve the suite's current owner-bundle contracts after the path-mirror removal:
  - keep the module-workflow bundle order anchored to `module-workflow-surface` first and `match-behavior-smoke` second;
  - keep the public-surface bundle order anchored to `public-api-surface`, `exported-symbol-surface`, then `pattern-object-surface`;
  - keep the existing `expected_fixture_path=` assertions and owner-manifest-id checks green by deriving their paths from the selector-owned tuples rather than retyping file literals.
- `tests/python/test_fixture_parity_support_contract.py` treats both new selectors as first-class shared registry entries:
  - extend `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` with exact filename tuples for `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR` and `PUBLIC_SURFACE_FIXTURE_SELECTOR`; and
  - keep the declared-selector coverage assertions green without adding another parallel selector registry or suite-local expectation table.
- Do not broaden this cleanup into `tests/python/test_parser_matrix_parity_suite.py`, fixture manifests under `tests/conformance/fixtures/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n 'CORRECTNESS_FIXTURES_ROOT / \"(module_workflow_surface|match_behavior_smoke|public_api_surface|exported_symbol_surface|pattern_object_surface)\\.py\"|MODULE_WORKFLOW_FIXTURE_PATH =|MATCH_BEHAVIOR_FIXTURE_PATH =' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR,
    PUBLIC_SURFACE_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_module_workflow_parity_suite as mod

module_paths = select_correctness_fixture_paths(
    MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR
)
public_paths = select_correctness_fixture_paths(PUBLIC_SURFACE_FIXTURE_SELECTOR)

assert tuple(path.name for path in module_paths) == (
    "module_workflow_surface.py",
    "match_behavior_smoke.py",
)
assert tuple(path.name for path in public_paths) == (
    "public_api_surface.py",
    "exported_symbol_surface.py",
    "pattern_object_surface.py",
)
assert tuple(bundle.manifest.path for bundle in (mod.MODULE_WORKFLOW_BUNDLE, mod.MATCH_BEHAVIOR_BUNDLE)) == module_paths
assert tuple(bundle.manifest.manifest_id for bundle in (mod.MODULE_WORKFLOW_BUNDLE, mod.MATCH_BEHAVIOR_BUNDLE)) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
assert tuple(bundle.manifest.path for bundle in mod.PUBLIC_SURFACE_BUNDLES) == public_paths
assert tuple(bundle.manifest.manifest_id for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    "public-api-surface",
    "exported-symbol-surface",
    "pattern-object-surface",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `python/rebar_harness/correctness.py`, `tests/python/test_module_workflow_parity_suite.py`, and `tests/python/test_fixture_parity_support_contract.py`.
- Prefer deleting the remaining raw path mirrors over adding another helper module, another suite-local selector table, or another manifest-id keyed wrapper.

## Notes
- `RBR-0823` is free in the current checkout:
  - `rg -n "RBR-0823|RBR-0824|RBR-0825|RBR-0826|RBR-0827" ops/state/backlog.md ops/state/current_status.md ops/tasks` returned only a historical mention inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`804 passed, 1 skipped in 0.63s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`284 passed in 0.34s`);
  - `bash -lc "! rg -n 'CORRECTNESS_FIXTURES_ROOT / \"(module_workflow_surface|match_behavior_smoke|public_api_surface|exported_symbol_surface|pattern_object_surface)\\.py\"|MODULE_WORKFLOW_FIXTURE_PATH =|MATCH_BEHAVIOR_FIXTURE_PATH =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on the remaining raw owner-path mirrors in that suite; and
  - `PYTHONPATH=python python3 - <<'PY'
try:
    from rebar_harness.correctness import (
        MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR,
        PUBLIC_SURFACE_FIXTURE_SELECTOR,
    )
except Exception as exc:
    print(type(exc).__name__, exc)
PY` currently fails with `ImportError: cannot import name 'MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR' from 'rebar_harness.correctness'`, which is the exact cleanup this task is meant to land.
- This cleanup follows the same selector-first simplification path as the recent sidecar removals:
  - `ops/tasks/done/RBR-0817-collapse-grouped-capture-fixture-sidecar-onto-owner-ordered-selector.md`
  - `ops/tasks/done/RBR-0819-add-grouped-replacement-selector-and-collapse-suite-sidecar.md`
  - `ops/tasks/done/RBR-0821-add-collection-replacement-selector-and-collapse-singleton-fixture-loads.md`

## Completion
- Added `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR = "module-workflow-surface"` and `PUBLIC_SURFACE_FIXTURE_SELECTOR = "public-surface"` to `python/rebar_harness/correctness.py`, and registered both selectors with the exact owner tuple order this suite already depended on.
- Switched `tests/python/test_module_workflow_parity_suite.py` to load the module-workflow/match pair and the public-surface trio through `select_correctness_fixture_paths(...)`, keeping the existing bundle order, manifest-id checks, and `expected_fixture_path=` assertions anchored to selector-owned tuples instead of raw `CORRECTNESS_FIXTURES_ROOT / ...` literals.
- Extended `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` in `tests/python/test_fixture_parity_support_contract.py` so the shared selector registry contract now covers both new surface selectors.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`804 passed, 1 skipped`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`286 passed`), the required `rg` absence check (no matches), and the Acceptance selector-order probe (`ok`).
