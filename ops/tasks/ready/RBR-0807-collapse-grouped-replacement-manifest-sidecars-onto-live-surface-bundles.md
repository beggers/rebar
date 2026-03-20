# RBR-0807: Collapse grouped replacement manifest sidecars onto live surface bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining grouped-replacement manifest-id sidecars from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Keep the grouped replacement parity owner on one canonical source of truth by deriving bundle-order and contract-target membership from `GROUPED_REPLACEMENT_TEMPLATE_SURFACE.bundles` instead of mirrored file-local constants.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines or references:
  - `GROUPED_REPLACEMENT_EXPECTED_MANIFEST_IDS`; or
  - `GROUPED_REPLACEMENT_TEMPLATE_CONTRACT_MANIFEST_IDS`.
- The grouped replacement ownership and contract checks stay explicit, but they now derive from the live grouped surface bundles instead of detached manifest-id tables:
  - the selected grouped replacement bundle order still resolves to `collection`, `named`, `grouped-alternation`, `nested-group`, `nested-group-alternation`, `quantified-nested-group`, then `nested-broader-range-wider-ranged-repeat...replacement-workflows`;
  - `test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit()` or its equivalent still proves the first grouped bundle is the selected two-row collection owner bundle and keeps the current case-level assertions intact; and
  - `_assert_grouped_replacement_fixture_bundle_contract(...)` still runs for the same five grouped manifests it covers today, but the gating condition is derived from the live grouped bundles rather than a second handwritten manifest-id set.
- Do not broaden into the open-ended or conditional replacement surfaces, supplemental replacement cases, callable replacement plumbing, fixture manifests, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'grouped_replacement_surface_keeps_selected_bundle_ownership_explicit or parity_suite_stays_aligned_with_published_correctness_fixture'`
  - `bash -lc "! rg -n 'GROUPED_REPLACEMENT_(EXPECTED_MANIFEST_IDS|TEMPLATE_CONTRACT_MANIFEST_IDS)' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_fixture_backed_replacement_parity_suite as mod
surface = mod.GROUPED_REPLACEMENT_TEMPLATE_SURFACE
bundle_ids = tuple(bundle.expected_manifest_id for bundle in surface.bundles)
assert bundle_ids == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
contract_bundle_ids = tuple(
    bundle.expected_manifest_id
    for bundle in surface.bundles
    if bundle.expected_manifest_id
    not in {
        "collection-replacement-workflows",
        "named-group-replacement-workflows",
    }
)
assert contract_bundle_ids == (
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Prefer deleting the mirrored manifest-id constants over adding another helper module, another registry, or another parallel ownership table.

## Notes
- `RBR-0807` is free in the current checkout:
  - `rg -n "RBR-0807|RBR-0808|RBR-0809|RBR-0810" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only one historical mention inside the completed `RBR-0805` notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and currently mirrored in the live checkout:
  - `rg -n 'GROUPED_REPLACEMENT_(EXPECTED_MANIFEST_IDS|TEMPLATE_CONTRACT_MANIFEST_IDS)' tests/python/test_fixture_backed_replacement_parity_suite.py` currently reports exactly the two manifest-id sidecars plus their two local consumers;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_fixture_backed_replacement_parity_suite as mod
surface = mod.GROUPED_REPLACEMENT_TEMPLATE_SURFACE
print(tuple(bundle.expected_manifest_id for bundle in surface.bundles))
print(mod.GROUPED_REPLACEMENT_EXPECTED_MANIFEST_IDS)
print(tuple(sorted(mod.GROUPED_REPLACEMENT_TEMPLATE_CONTRACT_MANIFEST_IDS)))
print(tuple(sorted(
    bundle.expected_manifest_id
    for bundle in surface.bundles
    if bundle.expected_manifest_id
    not in {
        mod.GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID,
        mod.GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
    }
)))
PY` currently prints identical bundle-order and contract-target tuples, showing both constants are mirrored state rather than independent contract sources; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'grouped_replacement_surface_keeps_selected_bundle_ownership_explicit or parity_suite_stays_aligned_with_published_correctness_fixture'` currently passes (`21 passed, 1145 deselected in 0.11s`).
- This follows the same owner-surface cleanup track as `RBR-0713` and `RBR-0785`: those tasks already moved grouped-replacement routing metadata and conditional replacement bundle specs onto canonical surface owners, and these two remaining grouped manifest-id tables are now the next bounded mirror to delete without changing parity behavior.
