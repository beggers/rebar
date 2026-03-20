# RBR-0805: Collapse default-only source-tree combined manifest entries onto live defaults

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the handwritten default-only manifest rows from the shared source-tree benchmark expectation registry in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Keep explicit registry data only for manifests that actually need nondefault combined-suite metadata, while preserving the current public zero-gap/empty-representative behavior for the default manifests through one live fallback path.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer stores pure `_combined_manifest_definition()` rows for these manifest ids:
  - `collection-replacement-boundary`
  - `literal-flag-boundary`
  - `grouped-segment-boundary`
  - `literal-alternation-boundary`
  - `grouped-alternation-callable-replacement-boundary`
  - `nested-group-alternation-boundary`
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
  - `optional-group-alternation-boundary`
  - `conditional-group-exists-boundary`
  - `conditional-group-exists-no-else-boundary`
  - `conditional-group-exists-empty-else-boundary`
  - `conditional-group-exists-empty-yes-else-boundary`
  - `conditional-group-exists-fully-empty-boundary`
- The combined-manifest helper path still behaves exactly as it does today for those manifests:
  - `source_tree_combined_case(manifest_id).manifest_expectation.known_gap_count == 0`
  - `source_tree_combined_case(manifest_id).manifest_expectation.representative_measured_workload_ids == ()`
  - `source_tree_combined_case(manifest_id).manifest_expectation.representative_known_gap_workload_ids == ()`
- Keep explicit override-bearing behavior intact for the manifests that really need it:
  - exclusion-only or exclusion-plus-metadata manifests like `compile-matrix` and `regression-matrix` still stay explicit;
  - zero-gap promotion, representative-id, known-gap, shape, fully-measured, and zero-gap-bytes-subset contracts still come from explicit definitions rather than implicit fallback; and
  - `source_tree_combined_target_manifest_ids()` still resolves to the published full-suite manifest ids minus only the explicitly excluded combined-base manifests.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'raw_manifest_expectations or manifest_gap_inventories or zero_gap_manifests or zero_default_public_manifest_expectations or literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps or zero_gap_manifest_representative_promotions or combined_target_manifest_ids_exclude_only_definition_owned_base_manifests'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import source_tree_combined_case
manifest_ids = (
    'collection-replacement-boundary',
    'literal-flag-boundary',
    'grouped-segment-boundary',
    'literal-alternation-boundary',
    'grouped-alternation-callable-replacement-boundary',
    'nested-group-alternation-boundary',
    'nested-group-replacement-boundary',
    'nested-group-callable-replacement-boundary',
    'optional-group-alternation-boundary',
    'conditional-group-exists-boundary',
    'conditional-group-exists-no-else-boundary',
    'conditional-group-exists-empty-else-boundary',
    'conditional-group-exists-empty-yes-else-boundary',
    'conditional-group-exists-fully-empty-boundary',
)
for manifest_id in manifest_ids:
    expectation = source_tree_combined_case(manifest_id).manifest_expectation
    assert expectation.known_gap_count == 0, (manifest_id, expectation)
    assert expectation.representative_measured_workload_ids == (), (manifest_id, expectation)
    assert expectation.representative_known_gap_workload_ids == (), (manifest_id, expectation)
print('ok')
PY`
  - `bash -lc "! rg -n '^    \\\"(collection-replacement-boundary|literal-flag-boundary|grouped-segment-boundary|literal-alternation-boundary|grouped-alternation-callable-replacement-boundary|nested-group-alternation-boundary|nested-group-replacement-boundary|nested-group-callable-replacement-boundary|optional-group-alternation-boundary|conditional-group-exists-boundary|conditional-group-exists-no-else-boundary|conditional-group-exists-empty-else-boundary|conditional-group-exists-empty-yes-else-boundary|conditional-group-exists-fully-empty-boundary)\\\": _combined_manifest_definition\\(\\),?$' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not broaden into `SOURCE_TREE_SCORECARD_EXPECTATIONS`, `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, benchmark workload manifests, harness implementation code, reports, README copy, or tracked project-state prose.
- Prefer deleting default-only registry rows and routing them through one existing/live fallback path over adding another parallel registry, another support module, or another handwritten manifest allowlist.

## Notes
- `RBR-0805` is free in the current checkout:
  - `rg -n "RBR-0805|RBR-0806|RBR-0807" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical references inside the completed `RBR-0803` task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
def default_only(expectation):
    return (
        not expectation.exclude_from_combined_targets
        and not expectation.promote_zero_gap_representatives
        and expectation.known_gap_workload_ids is None
        and expectation.representative_measured_workload_ids is None
        and expectation.representative_known_gap_workload_ids is None
        and expectation.fully_measured_expectation is None
        and expectation.shape_expectation is None
        and not expectation.zero_gap_bytes_representative_subsets
    )
print([
    manifest_id
    for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
    if default_only(expectation)
])
PY` currently reports those exact 14 manifest ids as pure default rows; and
  - the public fallback they currently restate is already zero-gap and empty-representative for all 14 ids, as confirmed by the acceptance probe above (`ok`).
- This is the next step after the earlier default-field cleanups (`RBR-0469` and `RBR-0470`): those tasks deleted default-valued fields inside manifest definitions, while this task deletes entire manifest entries that no longer carry any nondefault metadata at all.
