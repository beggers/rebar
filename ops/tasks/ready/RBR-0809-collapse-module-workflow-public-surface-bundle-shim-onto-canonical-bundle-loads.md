# RBR-0809: Collapse the module-workflow public-surface bundle shim onto canonical bundle loads

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the synthetic public-surface bundle rebuild in `tests/python/test_module_workflow_parity_suite.py`.
- Keep the public-surface parity checks on one canonical owner path by loading the three published manifests directly through `load_published_fixture_bundles(...)` instead of rebuilding `FixtureBundle`s just to fake a pattern-based contract.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or references:
  - `_public_surface_loader_token`; or
  - `PUBLIC_SURFACE_EXPECTED_TEXT_MODELS_BY_MANIFEST_ID`.
- `PUBLIC_SURFACE_BUNDLES` stops wrapping the three public-surface owner manifests in a per-bundle `build_fixture_bundle(...)` rebuild:
  - load `public_api_surface.py`, `exported_symbol_surface.py`, and `pattern_object_surface.py` directly through `load_published_fixture_bundles(...)`;
  - keep the public-surface contract anchored to case ids by using `_public_surface_case_contract_token` as the canonical token source; and
  - do not reintroduce another manifest-id keyed sidecar or another local bundle-spec layer.
- `test_public_surface_parity_suite_stays_aligned_with_published_fixtures()` or its equivalent still keeps the public-surface contract explicit without the synthetic bundle rebuild:
  - preserve the current manifest order `public-api-surface`, `exported-symbol-surface`, `pattern-object-surface`;
  - preserve the current published case order for each bundle by checking against `bundle.manifest.cases` or an equivalent direct owner-manifest source; and
  - keep the mixed `{"bytes", "str"}` text-model contract explicit for `pattern-object-surface` without routing that fact through a manifest-id keyed dictionary.
- Preserve the existing public-surface frontier and direct-test coverage behavior:
  - keep `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, `PATTERN_OBJECT_BUNDLE`, the public-surface frontier test, and the direct-test case-id bucket coverage intact; and
  - do not broaden into `tests/conformance/fixtures/`, `python/rebar_harness/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '_public_surface_loader_token|PUBLIC_SURFACE_EXPECTED_TEXT_MODELS_BY_MANIFEST_ID|PUBLIC_SURFACE_BUNDLES = tuple\\(|expected_patterns=frozenset\\(case\\.case_id for case in bundle\\.cases\\)|expected_case_ids=frozenset\\(case\\.case_id for case in bundle\\.cases\\)' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod
assert tuple(bundle.manifest.manifest_id for bundle in mod.PUBLIC_SURFACE_BUNDLES) == (
    "public-api-surface",
    "exported-symbol-surface",
    "pattern-object-surface",
)
for bundle in mod.PUBLIC_SURFACE_BUNDLES:
    case_ids = frozenset(case.case_id for case in bundle.cases)
    assert bundle.expected_patterns == case_ids
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
pattern_bundle = mod.PATTERN_OBJECT_BUNDLE
assert {case.text_model for case in pattern_bundle.cases} == {"bytes", "str"}
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the synthetic bundle rebuild and manifest-id keyed text-model sidecar over adding another support helper, another registry, or another abstraction layer.

## Notes
- `RBR-0809` is free in the current checkout:
  - `rg -n "RBR-0809|RBR-0810|RBR-0811|RBR-0812" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only one historical mention inside the completed `RBR-0807` notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`772 passed, 1 skipped in 0.59s`);
  - the negative `rg` acceptance command currently fails exactly on the synthetic public-surface shim, reporting `_public_surface_loader_token`, `PUBLIC_SURFACE_EXPECTED_TEXT_MODELS_BY_MANIFEST_ID`, and the `build_fixture_bundle(...)`-backed `PUBLIC_SURFACE_BUNDLES` block; and
  - the public-surface probe in Acceptance currently passes (`ok`), showing the rebuilt bundles are only restating manifest id order, case id order, and case-id-backed expected patterns that are already available from the loaded owner manifests.
- This follows the same post-JSON simplification direction as the recent parity-suite sidecar removals:
  - `ops/tasks/done/RBR-0797-collapse-generated-quantified-alternation-spec-sidecars-onto-live-bundle-metadata.md`
  - `ops/tasks/done/RBR-0799-collapse-generated-quantified-conditional-spec-sidecars-onto-live-bundle-metadata.md`
  - `ops/tasks/done/RBR-0807-collapse-grouped-replacement-manifest-sidecars-onto-live-surface-bundles.md`
