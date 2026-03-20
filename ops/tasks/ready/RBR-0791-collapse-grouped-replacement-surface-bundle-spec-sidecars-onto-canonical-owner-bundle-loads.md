# RBR-0791: Collapse grouped replacement surface bundle-spec sidecars onto canonical owner-bundle loads

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the last bespoke `FixtureBundleSpec(...)` / `load_fixture_bundles(...)` branch from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Rebuild `GROUPED_REPLACEMENT_TEMPLATE_SURFACE` from canonical published owner-bundle loads, matching the pattern already used by the other parity suites: load full published manifests through `load_published_fixture_bundles(...)`, then trim or restate only the file-local selected-frontier expectations that the surface still needs.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer imports or uses `FixtureBundleSpec` or `load_fixture_bundles(...)`.
- `ReplacementSurfaceSpec` in that file no longer carries the `bundle_specs` field, and `_load_surface(...)` no longer branches between two loader modes. Every replacement surface should start from `load_published_fixture_bundles(...)` over `selector_fixture_paths`.
- `GROUPED_REPLACEMENT_TEMPLATE_SURFACE` loads these seven owner manifests through `selector_fixture_paths` and a single canonical owner-bundle path:
  - `collection_replacement_workflows.py`
  - `named_group_replacement_workflows.py`
  - `grouped_alternation_replacement_workflows.py`
  - `nested_group_replacement_workflows.py`
  - `nested_group_alternation_replacement_workflows.py`
  - `quantified_nested_group_replacement_workflows.py`
  - `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
- Preserve the current selected-frontier behavior after the cleanup:
  - the collection bundle still selects exactly `GROUPED_REPLACEMENT_COLLECTION_CASE_IDS`;
  - the named-group bundle still selects exactly `GROUPED_REPLACEMENT_NAMED_CASE_IDS`;
  - the nested-group-alternation bundle still selects exactly `NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS`;
  - the mixed-text broader-range bundle still selects the same 16 numbered and named case ids it selects today;
  - the grouped-alternation, nested-group, and quantified-nested-group bundles remain full-manifest bundles; and
  - the grouped replacement surface keeps the same bundle order, compile-pattern contract, template-expand manifest coverage, and direct-test coverage behavior it has now.
- Update the grouped replacement contract checks that currently read `surface.spec.bundle_specs` so they derive their expectations from explicit local manifest-id or case-id constants, or from the loaded bundles themselves, without reintroducing another sidecar registry.
- Keep scope structural only:
  - prefer deleting the mirrored sidecars over adding another shared registry or another support layer;
  - if a helper is useful, keep it file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`; and
  - do not edit `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, benchmarks, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import load_published_fixture_bundles
import tests.python.test_fixture_backed_replacement_parity_suite as mod

paths = (
    CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT / "named_group_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT / "grouped_alternation_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT / "nested_group_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT / "nested_group_alternation_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT / "quantified_nested_group_replacement_workflows.py",
    CORRECTNESS_FIXTURES_ROOT
    / "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
)

bundles = load_published_fixture_bundles(paths, pattern_extractor=mod.case_pattern)
assert tuple(bundle.expected_manifest_id for bundle in bundles) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    mod.NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
)
print("ok")
PY`
  - `python3 - <<'PY'
from pathlib import Path

text = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text()
for needle in ("FixtureBundleSpec", "load_fixture_bundles(", "bundle_specs"):
    assert needle not in text, needle
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Do not broaden into redesigning `FixtureBundleSpec` support in `tests/python/fixture_parity_support.py`, deleting its contract tests, or changing published fixture contents.

## Notes
- `RBR-0791` is free in the current checkout:
  - `rg -n "RBR-0791|RBR-0792|RBR-0793|RBR-0794|RBR-0795" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - the task queues do not already contain an `RBR-0791` file.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and viable in the current checkout:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/python/test_fixture_parity_support_contract.py` currently passes (`1403 passed in 1.10s`);
  - the owner-bundle probe in Acceptance already passes (`ok`), showing the grouped replacement owner manifests load cleanly through the canonical published-bundle path; and
  - the structural Acceptance probe currently fails exactly on this cleanup with `AssertionError: FixtureBundleSpec` because the file still contains the last sidecar loader branch.
- This stays on the same post-JSON replacement-harness cleanup track as:
  - `ops/tasks/done/RBR-0785-collapse-conditional-replacement-bundle-spec-sidecars-onto-canonical-selector-bundles.md`
  - `ops/tasks/done/RBR-0787-collapse-open-ended-replacement-bundle-spec-sidecars-onto-canonical-selector-bundles.md`
  - `ops/tasks/done/RBR-0789-collapse-replacement-contract-bundle-spec-sidecars-onto-canonical-owner-bundle-loads.md`
