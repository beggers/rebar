# RBR-0865: Collapse conditional-group manifest partitions onto live bundle classification

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the handwritten conditional manifest-partition tables from `tests/python/test_conditional_group_exists_parity_suite.py` so the suite derives its base, quantified, and nested-or-alternation bundle groups from the already loaded `FIXTURE_BUNDLES` instead of maintaining detached manifest-id tuples plus parallel bundle tuples.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` stops defining or reading these detached manifest-id and bundle partition mirrors:
  - `BASE_MANIFEST_IDS`
  - `QUANTIFIED_MANIFEST_IDS`
  - `NESTED_OR_ALTERNATION_MANIFEST_IDS`
  - `BASE_BUNDLES`
  - `QUANTIFIED_BUNDLES`
  - `NESTED_OR_ALTERNATION_BUNDLES`
- The suite derives the same three bundle partitions directly from live `FIXTURE_BUNDLES` metadata, using tiny file-local classification and ordering helpers if needed rather than handwritten manifest-id tables.
- Preserve the current effective partition membership and order exactly:
  - the base partition still resolves to `optional-group-conditional-workflows`, `conditional-group-exists-workflows`, `conditional-group-exists-no-else-workflows`, `conditional-group-exists-empty-else-workflows`, `conditional-group-exists-empty-yes-else-workflows`, and `conditional-group-exists-fully-empty-workflows`;
  - the quantified partition still resolves to `conditional-group-exists-quantified-workflows`, `conditional-group-exists-quantified-alternation-workflows`, `conditional-group-exists-no-else-quantified-workflows`, `conditional-group-exists-empty-else-quantified-workflows`, `conditional-group-exists-empty-yes-else-quantified-workflows`, and `conditional-group-exists-fully-empty-quantified-workflows`; and
  - the nested-or-alternation partition still resolves to `conditional-group-exists-nested-workflows`, `conditional-group-exists-no-else-nested-workflows`, `conditional-group-exists-empty-else-nested-workflows`, `conditional-group-exists-empty-yes-else-nested-workflows`, `conditional-group-exists-fully-empty-nested-workflows`, `conditional-group-exists-alternation-workflows`, `conditional-group-exists-no-else-alternation-workflows`, `conditional-group-exists-empty-else-alternation-workflows`, `conditional-group-exists-empty-yes-else-alternation-workflows`, and `conditional-group-exists-fully-empty-alternation-workflows`.
- Keep the downstream case partitions behaviorally unchanged after the mirror removal:
  - `CORE_CONDITIONAL_COMPILE_CASES`, `NESTED_OR_ALTERNATION_COMPILE_CASES`, `BASE_MODULE_CASES`, `QUANTIFIED_MODULE_CASES`, `NESTED_OR_ALTERNATION_MODULE_CASES`, `BASE_PATTERN_CASES`, `QUANTIFIED_PATTERN_CASES`, and `NESTED_OR_ALTERNATION_PATTERN_CASES` must still derive from the same ordered bundle slices.
- Do not broaden scope beyond this cleanup:
  - do not change correctness fixtures, shared correctness selectors, harness modules, reports, README copy, or tracked project-state prose; and
  - do not widen into replacement-conditioned conditional suites, benchmark owners, or new shared helper modules in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '^(BASE_MANIFEST_IDS|QUANTIFIED_MANIFEST_IDS|NESTED_OR_ALTERNATION_MANIFEST_IDS|BASE_BUNDLES|QUANTIFIED_BUNDLES|NESTED_OR_ALTERNATION_BUNDLES) =' tests/python/test_conditional_group_exists_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_conditional_group_exists_parity_suite as mod

VARIANT_ORDER = {
    "plain": 0,
    "no-else": 1,
    "empty-else": 2,
    "empty-yes-else": 3,
    "fully-empty": 4,
}
GROUP_ORDER = {"nested": 0, "alternation": 1}


def manifest_variant(manifest_id: str) -> str:
    if manifest_id == "optional-group-conditional-workflows":
        return "plain"
    for variant in ("empty-yes-else", "empty-else", "fully-empty", "no-else"):
        if f"conditional-group-exists-{variant}-" in manifest_id:
            return variant
    return "plain"


def manifest_group(manifest_id: str) -> str:
    if manifest_id == "optional-group-conditional-workflows":
        return "base"
    if "-quantified-" in manifest_id:
        return "quantified"
    if "-nested-" in manifest_id:
        return "nested"
    if "-alternation-" in manifest_id:
        return "alternation"
    return "base"


base = tuple(
    bundle.expected_manifest_id
    for bundle in sorted(
        [b for b in mod.FIXTURE_BUNDLES if manifest_group(b.expected_manifest_id) == "base"],
        key=lambda bundle: (
            0 if bundle.expected_manifest_id == "optional-group-conditional-workflows" else 1,
            VARIANT_ORDER[manifest_variant(bundle.expected_manifest_id)],
            bundle.expected_manifest_id,
        ),
    )
)
quantified = tuple(
    bundle.expected_manifest_id
    for bundle in sorted(
        [b for b in mod.FIXTURE_BUNDLES if manifest_group(b.expected_manifest_id) == "quantified"],
        key=lambda bundle: (
            VARIANT_ORDER[manifest_variant(bundle.expected_manifest_id)],
            0 if bundle.expected_manifest_id == "conditional-group-exists-quantified-workflows" else 1,
            0 if bundle.expected_manifest_id == "conditional-group-exists-quantified-alternation-workflows" else 1,
            bundle.expected_manifest_id,
        ),
    )
)
nested_or_alternation = tuple(
    bundle.expected_manifest_id
    for bundle in sorted(
        [
            b
            for b in mod.FIXTURE_BUNDLES
            if manifest_group(b.expected_manifest_id) in {"nested", "alternation"}
        ],
        key=lambda bundle: (
            GROUP_ORDER[manifest_group(bundle.expected_manifest_id)],
            VARIANT_ORDER[manifest_variant(bundle.expected_manifest_id)],
            bundle.expected_manifest_id,
        ),
    )
)

assert base == (
    "optional-group-conditional-workflows",
    "conditional-group-exists-workflows",
    "conditional-group-exists-no-else-workflows",
    "conditional-group-exists-empty-else-workflows",
    "conditional-group-exists-empty-yes-else-workflows",
    "conditional-group-exists-fully-empty-workflows",
)
assert quantified == (
    "conditional-group-exists-quantified-workflows",
    "conditional-group-exists-quantified-alternation-workflows",
    "conditional-group-exists-no-else-quantified-workflows",
    "conditional-group-exists-empty-else-quantified-workflows",
    "conditional-group-exists-empty-yes-else-quantified-workflows",
    "conditional-group-exists-fully-empty-quantified-workflows",
)
assert nested_or_alternation == (
    "conditional-group-exists-nested-workflows",
    "conditional-group-exists-no-else-nested-workflows",
    "conditional-group-exists-empty-else-nested-workflows",
    "conditional-group-exists-empty-yes-else-nested-workflows",
    "conditional-group-exists-fully-empty-nested-workflows",
    "conditional-group-exists-alternation-workflows",
    "conditional-group-exists-no-else-alternation-workflows",
    "conditional-group-exists-empty-else-alternation-workflows",
    "conditional-group-exists-empty-yes-else-alternation-workflows",
    "conditional-group-exists-fully-empty-alternation-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the mirrored conditional manifest-partition tables inside the parity owner, not to reinterpret conditional semantics, change which manifests the suite covers, or move another family onto a new selector path.
- Keep scope limited to `tests/python/test_conditional_group_exists_parity_suite.py`.

## Notes
- `RBR-0865` is the next available architecture task id in the current checkout:
  - `RBR-0864` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0865`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and already viable in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.45s`);
  - the partition-order probe in Acceptance already passes in the current checkout (`ok`), confirming the same three bundle groups can already be recovered from live `FIXTURE_BUNDLES` metadata without the handwritten manifest-id tables; and
  - `bash -lc "! rg -n '^(BASE_MANIFEST_IDS|QUANTIFIED_MANIFEST_IDS|NESTED_OR_ALTERNATION_MANIFEST_IDS|BASE_BUNDLES|QUANTIFIED_BUNDLES|NESTED_OR_ALTERNATION_BUNDLES) =' tests/python/test_conditional_group_exists_parity_suite.py"` currently fails exactly on this cleanup because those mirrored tables still exist.
- This stays off the active benchmark feature frontier:
  - the only ready feature task is `RBR-0864`, which is a `module_boundary.py` benchmark catch-up task; and
  - this cleanup stays confined to the conditional correctness parity owner instead of introducing another edit on the current benchmark-owner file path.
