# RBR-0817: Collapse the grouped-capture fixture sidecar onto an owner-ordered selector

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the grouped-capture parity suite's handwritten eight-file fixture path sidecar from `tests/python/test_grouped_capture_parity_suite.py`.
- Keep that suite anchored to the correctness harness through `GROUPED_CAPTURE_FIXTURE_SELECTOR`, while preserving the suite's current owner-order bundle contract.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` keeps `GROUPED_CAPTURE_FIXTURE_SELECTOR` but changes its registered file order to match the grouped-capture suite's current owner order exactly, rather than routing through `_sorted_published_fixture_subset(...)`:
  - `grouped_match_workflows.py`
  - `named_group_workflows.py`
  - `grouped_segment_workflows.py`
  - `grouped_alternation_workflows.py`
  - `optional_group_workflows.py`
  - `optional_group_alternation_workflows.py`
  - `nested_group_workflows.py`
  - `nested_group_alternation_workflows.py`
- `tests/python/test_grouped_capture_parity_suite.py` no longer defines or references the file-local `CORRECTNESS_FIXTURES_ROOT / ...` tuple used only to load that slice.
- `tests/python/test_grouped_capture_parity_suite.py` imports and uses `GROUPED_CAPTURE_FIXTURE_SELECTOR` plus `select_correctness_fixture_paths(...)` from `rebar_harness.correctness` to build `FIXTURE_BUNDLES`.
- Preserve the suite's existing owner-order contract and manifest anchors after the sidecar removal:
  - `test_fixture_bundles_load_expected_published_owner_order` must still assert the same path-name order and manifest-id order it does today;
  - `GROUPED_MATCH_FIXTURE_BUNDLE` and `GROUPED_SEGMENT_FIXTURE_BUNDLE` must still resolve by manifest id; and
  - do not broaden the task into fixture manifests, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `bash -lc "! rg -n 'CORRECTNESS_FIXTURES_ROOT / \"(grouped_match_workflows|named_group_workflows|grouped_segment_workflows|grouped_alternation_workflows|optional_group_workflows|optional_group_alternation_workflows|nested_group_workflows|nested_group_alternation_workflows)\\.py\"' tests/python/test_grouped_capture_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_grouped_capture_parity_suite as mod

assert tuple(bundle.manifest.path for bundle in mod.FIXTURE_BUNDLES) == (
    select_correctness_fixture_paths(GROUPED_CAPTURE_FIXTURE_SELECTOR)
)
assert tuple(bundle.manifest.path.name for bundle in mod.FIXTURE_BUNDLES) == (
    "grouped_match_workflows.py",
    "named_group_workflows.py",
    "grouped_segment_workflows.py",
    "grouped_alternation_workflows.py",
    "optional_group_workflows.py",
    "optional_group_alternation_workflows.py",
    "nested_group_workflows.py",
    "nested_group_alternation_workflows.py",
)
assert tuple(bundle.manifest.manifest_id for bundle in mod.FIXTURE_BUNDLES) == (
    "grouped-match-workflows",
    "named-group-workflows",
    "grouped-segment-workflows",
    "grouped-alternation-workflows",
    "optional-group-workflows",
    "optional-group-alternation-workflows",
    "nested-group-workflows",
    "nested-group-alternation-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `python/rebar_harness/correctness.py` and `tests/python/test_grouped_capture_parity_suite.py`.
- Prefer deleting the file-local path mirror over adding another suite-local order shim or selector map.

## Notes
- `RBR-0817` is free in the current checkout:
  - `rg -n "RBR-0817|RBR-0818|RBR-0819|RBR-0820" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only a historical mention inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`436 passed in 0.30s`);
  - `bash -lc "! rg -n 'CORRECTNESS_FIXTURES_ROOT / \"(grouped_match_workflows|named_group_workflows|grouped_segment_workflows|grouped_alternation_workflows|optional_group_workflows|optional_group_alternation_workflows|nested_group_workflows|nested_group_alternation_workflows)\\.py\"' tests/python/test_grouped_capture_parity_suite.py"` currently fails exactly on the suite's duplicated path tuple; and
  - the selector-order probe in Acceptance currently fails only because `GROUPED_CAPTURE_FIXTURE_SELECTOR` is alphabetized differently from the suite's owner order (`needs-order-fix`), which is the exact cleanup this task is meant to land.
- The selector-order wrinkle is already isolated:
  - `rg -n "GROUPED_CAPTURE_FIXTURE_SELECTOR" .` shows the selector is only defined in `python/rebar_harness/correctness.py` and not consumed anywhere else yet; and
  - `test_grouped_capture_parity_suite.py` already asserts the owner-order bundle contract explicitly, so the selector should carry that order instead of forcing the suite to duplicate it locally.
