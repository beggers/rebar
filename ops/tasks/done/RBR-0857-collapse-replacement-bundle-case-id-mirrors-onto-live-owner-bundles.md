# RBR-0857: Collapse replacement bundle case-id mirrors onto live owner bundles

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the remaining replacement-suite case-id mirror tuples from `tests/python/test_fixture_backed_replacement_parity_suite.py` where the loaded owner bundles already carry the canonical ordered case set.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` stops defining or reading these detached mirror tuples:
  - `GROUPED_REPLACEMENT_NAMED_CASE_IDS`
  - `NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS`
  - `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_CASE_IDS`
- The named-group, nested-group-alternation, and broader-range wider-ranged-repeat replacement assertions derive their ordered selected case ids directly from the already loaded owner bundles or existing bundle-derived helpers instead of routing through handwritten top-level tuples.
- Preserve the current bundle ownership and selected-frontier behavior exactly while deleting those mirrors:
  - keep `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS` in place, because `_grouped_replacement_template_bundles(...)` still uses it to carve the explicit two-row collection subset out of the larger `collection-replacement-workflows` owner manifest;
  - keep `_grouped_replacement_template_bundles(...)`, `_expected_selected_replacement_case_ids(...)`, `_expected_uncovered_replacement_case_ids(...)`, `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, and `BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE` behaviorally unchanged apart from sourcing the named/nested/wider-ranged ordered ids from live bundle rows;
  - keep the named replacement bundle ordered as `module-sub-template-named-group-str`, `module-subn-template-named-group-str`, `pattern-sub-template-named-group-str`, `pattern-subn-template-named-group-str`;
  - keep the nested-group-alternation wrapper-template slice anchored to `module-sub-template-nested-group-alternation-numbered-wrapper-str` and `pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str`; and
  - keep the broader-range wider-ranged-repeat mixed-text bundle selected frontier unchanged at the current sixteen str/bytes case ids and still fully covered by `_expected_selected_replacement_case_ids(surface, manifest_id=...)`.
- Do not broaden scope beyond this mirror deletion:
  - do not change correctness fixtures, shared fixture-support helpers, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose; and
  - do not retune the grouped collection subset, pending-bytes follow-on routing, replacement parity semantics, or direct-test bucket coverage in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^(GROUPED_REPLACEMENT_NAMED_CASE_IDS|NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_CASE_IDS) =' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import published_fixture_bundle_by_manifest_id
import tests.python.test_fixture_backed_replacement_parity_suite as mod

surface = mod.GROUPED_REPLACEMENT_TEMPLATE_SURFACE
named_bundle = published_fixture_bundle_by_manifest_id(
    surface.bundles,
    mod.GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
)
nested_alt_bundle = published_fixture_bundle_by_manifest_id(
    surface.bundles,
    mod.GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
)
manifest_id = mod.NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID
wider_bundle = mod.BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE

assert tuple(case.case_id for case in named_bundle.cases) == (
    "module-sub-template-named-group-str",
    "module-subn-template-named-group-str",
    "pattern-sub-template-named-group-str",
    "pattern-subn-template-named-group-str",
)
assert tuple(case.case_id for case in nested_alt_bundle.cases) == (
    "module-sub-template-nested-group-alternation-numbered-outer-str",
    "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    "module-sub-template-nested-group-alternation-numbered-wrapper-str",
    "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
)
assert tuple(case.case_id for case in wider_bundle.cases) == (
    mod._expected_selected_replacement_case_ids(surface, manifest_id=manifest_id)
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete three mirrored ownership tables inside the replacement parity owner, not to reinterpret replacement semantics, alter bundle selection, or introduce another helper layer.
- Keep scope limited to `tests/python/test_fixture_backed_replacement_parity_suite.py`.

## Notes
- `RBR-0857` is the next available architecture task id in the current checkout:
  - `RBR-0856` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0857`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1166 passed in 0.89s`);
  - the task-local probe in Acceptance already passes in the current checkout (`ok`), confirming the named, nested-group-alternation, and broader-range wider-ranged-repeat owner bundles already expose the exact ordered selected case ids without the top-level mirror tuples; and
  - `bash -lc "! rg -n '^(GROUPED_REPLACEMENT_NAMED_CASE_IDS|NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_CASE_IDS) =' tests/python/test_fixture_backed_replacement_parity_suite.py"` currently fails exactly on this cleanup because those mirrored tuples still exist.
- This stays on the same post-JSON parity-harness simplification track as the recent sidecar removals instead of opening another harness direction:
  - `RBR-0841` already collapsed replacement pytest-param sidecars onto live surfaces; and
  - this follow-on only removes the remaining named/nested/wider-ranged ordered case-id mirrors that duplicate live owner bundle order in the same replacement parity file.

## Completion
- 2026-03-21: Removed `GROUPED_REPLACEMENT_NAMED_CASE_IDS`, `NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS`, and `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_CASE_IDS` from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Rewired the named-group, nested-group-alternation, and broader-range wider-ranged-repeat assertions to read ordered case ids from the live owner bundles or the existing `_expected_selected_replacement_case_ids(...)` helper without changing grouped collection ownership, wrapper-anchor assertions, or mixed-text frontier behavior.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` (`1166 passed in 0.93s`), `bash -lc "! rg -n '^(GROUPED_REPLACEMENT_NAMED_CASE_IDS|NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS|NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_CASE_IDS) =' tests/python/test_fixture_backed_replacement_parity_suite.py"` (passes with no matches), and the task-local import/order probe from Acceptance (`ok`).
