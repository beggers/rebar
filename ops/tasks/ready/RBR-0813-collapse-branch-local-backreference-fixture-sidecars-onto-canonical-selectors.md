Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the branch-local backreference parity suite's handwritten fixture filename sidecars in `tests/python/test_branch_local_backreference_parity_suite.py`.
- Keep that suite anchored to the correctness harness's canonical fixture selectors by loading the simple backreference and branch-local backreference slices through `select_correctness_fixture_paths(...)` instead of mirroring published fixture filenames locally.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` no longer defines or references:
  - `BRANCH_LOCAL_BACKREFERENCE_FIXTURE_NAMES`;
  - `WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES`; or
  - the `CORRECTNESS_FIXTURES_ROOT / fixture_name` tuple-comprehension sidecar used only to rebuild those published slices.
- `FIXTURE_BUNDLES` loads from the correctness harness selectors instead of handwritten filename tuples:
  - import and use `BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR`, `SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR`, and `select_correctness_fixture_paths` from `rebar_harness.correctness`;
  - build the published bundle load paths from those selectors rather than a local filename table; and
  - do not add another filename tuple, manifest-id keyed selector map, or ordering shim just to restate the same canonical slice.
- Preserve the existing whole-manifest and manifest-id anchored coverage behavior without the local filename sidecars:
  - keep `NAMED_BACKREFERENCE_BUNDLE`, `NUMBERED_BACKREFERENCE_BUNDLE`, and `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES`;
  - keep the explicit manifest-id lookups for `QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, `NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE`, and `NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE`; and
  - keep the direct-bytes follow-on routing, generated parity specs, and whole-manifest pattern-call order checks intact without broadening into `python/rebar_harness/correctness.py`, fixture manifests, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `bash -lc "! rg -n 'BRANCH_LOCAL_BACKREFERENCE_FIXTURE_NAMES|WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_branch_local_backreference_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_branch_local_backreference_parity_suite as mod

simple_paths = select_correctness_fixture_paths(SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR)
branch_paths = select_correctness_fixture_paths(
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR
)
assert tuple(bundle.manifest.path.name for bundle in mod.WHOLE_MANIFEST_BACKREFERENCE_BUNDLES) == tuple(
    path.name for path in simple_paths
)
assert {bundle.manifest.path.name for bundle in mod.FIXTURE_BUNDLES} == {
    path.name for path in simple_paths + branch_paths
}
assert tuple(bundle.expected_manifest_id for bundle in mod.WHOLE_MANIFEST_BACKREFERENCE_BUNDLES) == (
    "named-backreference-workflows",
    "numbered-backreference-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `tests/python/test_branch_local_backreference_parity_suite.py`.
- Prefer deleting the handwritten selector mirrors over adding another helper, another registry, or another compatibility shim.

## Notes
- `RBR-0813` is free in the current checkout:
  - `rg -n "RBR-0813|RBR-0814|RBR-0815|RBR-0816" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only the historical mention embedded in the completed `RBR-0811` notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.78s`);
  - `bash -lc "! rg -n 'BRANCH_LOCAL_BACKREFERENCE_FIXTURE_NAMES|WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_branch_local_backreference_parity_suite.py"` currently fails exactly on the local filename tuples plus the tuple-comprehension load site; and
  - the selector coverage probe in Acceptance currently passes (`ok`), showing the suite's published manifest surface is already covered by the existing `SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR` plus `BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR`.
- The selector order wrinkle is already architecturally contained in the suite:
  - `select_correctness_fixture_paths(BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR)` returns the branch-local manifest files in canonical sorted order rather than the suite's current local tuple order; but
  - this module resolves its important published anchors by manifest id and keeps the whole-manifest backreference order explicit through `WHOLE_MANIFEST_BACKREFERENCE_BUNDLES`, so this cleanup should delete the filename sidecars instead of preserving the broader local path order as another duplicate contract.
