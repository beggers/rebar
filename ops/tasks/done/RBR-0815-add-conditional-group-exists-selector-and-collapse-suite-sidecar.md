# RBR-0815: Add a conditional-group-exists fixture selector and collapse the suite sidecar

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the handwritten conditional fixture filename sidecar from `tests/python/test_conditional_group_exists_parity_suite.py`.
- Keep that parity suite anchored to the correctness harness through one canonical selector in `python/rebar_harness/correctness.py`, while preserving the suite's existing base, quantified, and nested/alternation bundle-group order.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exports a dedicated selector for this surface:
  - add `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR = "conditional-group-exists"`; and
  - register that selector in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` with the exact 22-fixture order the parity suite currently uses, rather than routing through `_sorted_published_fixture_subset(...)`.
- `tests/python/test_conditional_group_exists_parity_suite.py` no longer defines or references:
  - `CONDITIONAL_FIXTURE_NAMES`; or
  - the `CORRECTNESS_FIXTURES_ROOT / fixture_name` tuple-comprehension sidecar used only to rebuild that slice.
- `FIXTURE_BUNDLES` in `tests/python/test_conditional_group_exists_parity_suite.py` loads from the new correctness-harness selector instead of the local filename tuple:
  - import and use `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR` plus `select_correctness_fixture_paths` from `rebar_harness.correctness`;
  - keep `pattern_extractor=str_case_pattern`; and
  - do not add another file-local filename tuple, manifest-id keyed selector shim, or reordered bundle wrapper.
- Preserve the suite's current grouping semantics and manifest anchors after the sidecar removal:
  - `BASE_BUNDLES` must still cover, in order, `optional-group-conditional-workflows`, `conditional-group-exists-workflows`, `conditional-group-exists-no-else-workflows`, `conditional-group-exists-empty-else-workflows`, `conditional-group-exists-empty-yes-else-workflows`, and `conditional-group-exists-fully-empty-workflows`;
  - `QUANTIFIED_BUNDLES` must still cover, in order, `conditional-group-exists-quantified-workflows`, `conditional-group-exists-quantified-alternation-workflows`, `conditional-group-exists-no-else-quantified-workflows`, `conditional-group-exists-empty-else-quantified-workflows`, `conditional-group-exists-empty-yes-else-quantified-workflows`, and `conditional-group-exists-fully-empty-quantified-workflows`; and
  - `NESTED_ALTERNATION_BUNDLES` must still cover, in order, `conditional-group-exists-nested-workflows`, `conditional-group-exists-no-else-nested-workflows`, `conditional-group-exists-empty-else-nested-workflows`, `conditional-group-exists-empty-yes-else-nested-workflows`, `conditional-group-exists-fully-empty-nested-workflows`, `conditional-group-exists-alternation-workflows`, `conditional-group-exists-no-else-alternation-workflows`, `conditional-group-exists-empty-else-alternation-workflows`, `conditional-group-exists-empty-yes-else-alternation-workflows`, and `conditional-group-exists-fully-empty-alternation-workflows`.
- Preserve the existing manifest-id anchored conditional follow-on coverage:
  - keep `QUANTIFIED_CONDITIONAL_BUNDLE`, `QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE`, `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS`, and the generated compile-anchor assertions tied to the same manifest ids they use today; and
  - do not broaden into fixture manifests under `tests/conformance/fixtures/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n 'CONDITIONAL_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_conditional_group_exists_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_conditional_group_exists_parity_suite as mod

assert tuple(bundle.manifest.path for bundle in mod.FIXTURE_BUNDLES) == (
    select_correctness_fixture_paths(CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR)
)
assert tuple(bundle.manifest.manifest_id for bundle in mod.BASE_BUNDLES) == (
    "optional-group-conditional-workflows",
    "conditional-group-exists-workflows",
    "conditional-group-exists-no-else-workflows",
    "conditional-group-exists-empty-else-workflows",
    "conditional-group-exists-empty-yes-else-workflows",
    "conditional-group-exists-fully-empty-workflows",
)
assert tuple(bundle.manifest.manifest_id for bundle in mod.QUANTIFIED_BUNDLES) == (
    "conditional-group-exists-quantified-workflows",
    "conditional-group-exists-quantified-alternation-workflows",
    "conditional-group-exists-no-else-quantified-workflows",
    "conditional-group-exists-empty-else-quantified-workflows",
    "conditional-group-exists-empty-yes-else-quantified-workflows",
    "conditional-group-exists-fully-empty-quantified-workflows",
)
assert tuple(
    bundle.manifest.manifest_id for bundle in mod.NESTED_ALTERNATION_BUNDLES
) == (
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
- Keep this cleanup limited to `python/rebar_harness/correctness.py` and `tests/python/test_conditional_group_exists_parity_suite.py`.
- Prefer deleting the local filename mirror over adding another file-local shim or another duplicate selector table.

## Notes
- `RBR-0815` is free in the current checkout:
  - `rg -n "RBR-0815|RBR-0816|RBR-0817|RBR-0818" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only a historical mention inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports a clean worktree and no last-cycle anomalies; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.44s`);
  - `bash -lc "! rg -n 'CONDITIONAL_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_conditional_group_exists_parity_suite.py"` currently fails exactly on the local filename tuple plus the tuple-comprehension load site; and
  - the task's selector-order probe currently fails only because `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR` does not exist yet, which is the exact cleanup this task is meant to land.
- A simple sorted-subset selector is not sufficient for this suite:
  - the suite currently slices `FIXTURE_BUNDLES` into `BASE_BUNDLES`, `QUANTIFIED_BUNDLES`, and `NESTED_ALTERNATION_BUNDLES` by position; and
  - the published-full-suite order for these 22 manifests does not match the current suite order, so the new selector must preserve the suite's existing grouped order explicitly instead of routing through the alphabetizing helper.

## Completion
- Added `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR` to `python/rebar_harness/correctness.py` with the exact 22-manifest order used by the parity suite, and switched `tests/python/test_conditional_group_exists_parity_suite.py` to load fixture paths through `select_correctness_fixture_paths(...)` instead of a duplicated local filename tuple.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`, `bash -lc "! rg -n 'CONDITIONAL_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_conditional_group_exists_parity_suite.py"`, and the task's selector-order probe script (`ok`).
