# RBR-0793: Delete dead spec-based fixture bundle loader plumbing

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the last dead spec-driven fixture-bundle loader layer from `tests/python/fixture_parity_support.py`.
- Retarget the surviving contract coverage in `tests/python/test_fixture_parity_support_contract.py` onto the canonical helpers that the parity suites still use: `build_fixture_bundle(...)`, `load_fixture_manifest(...)`, and `load_published_fixture_bundles(...)`.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` no longer defines `FixtureBundleSpec` or `load_fixture_bundles(...)`.
- `tests/python/test_fixture_parity_support_contract.py` no longer imports or references `FixtureBundleSpec` or `load_fixture_bundles(...)`.
- Preserve the surviving public support surface and its behavior:
  - keep `FixtureBundle`, `build_fixture_bundle(...)`, `load_published_fixture_bundles(...)`, `published_fixture_bundle_by_manifest_id(...)`, and the existing bundle-contract assertions intact;
  - keep the contract coverage for full-manifest bundle derivation, selected-row bundle construction, ordered-case behavior, duplicate-case rejection, expected-case-id handling, expected-text-model handling, and manifest-id derivation; and
  - rebuild any selected-row contract helpers directly from loaded manifests plus `build_fixture_bundle(...)` rather than reintroducing another sidecar spec type or another loader layer.
- Keep scope structural only:
  - prefer deleting the dead loader over adding a replacement abstraction;
  - if helper functions remain useful in `tests/python/test_fixture_parity_support_contract.py`, keep them file-local; and
  - do not edit fixture manifests under `tests/conformance/fixtures/`, harness code under `python/rebar_harness/`, benchmarks, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n 'FixtureBundleSpec|load_fixture_bundles\\(' tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup limited to the dead spec-loader plumbing in the shared parity-support module and its contract suite.
- Do not broaden into changing live parity suites that already use `load_published_fixture_bundles(...)` or `build_fixture_bundle(...)`.

## Notes
- `RBR-0793` is free in the current checkout:
  - `rg -n "RBR-0793|RBR-0794|RBR-0795" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` do not already contain an `RBR-0793` file.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both an architecture task and a feature task cleanly, with no inherited-dirty or commit-path anomaly recorded.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and isolated in the live checkout:
  - `rg -n "FixtureBundleSpec|load_fixture_bundles\\(" tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/python -g '*.py'` only reports the support module and the contract suite, so no live parity suite still depends on the spec-based loader;
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`253 passed in 0.31s`); and
  - `python3 - <<'PY'
from pathlib import Path
text = Path("tests/python/fixture_parity_support.py").read_text()
for needle in ("class FixtureBundleSpec", "def load_fixture_bundles("):
    assert needle in text, needle
print("ok")
PY` currently passes (`ok`), showing the dead layer is still present and making the structural acceptance meaningful.
- This is the next simplification after the recent owner-bundle cleanup track:
  - `ops/tasks/done/RBR-0782-collapse-remaining-owner-manifest-loader-wrappers-onto-canonical-bundle-loads.md`
  - `ops/tasks/done/RBR-0789-collapse-replacement-contract-bundle-spec-sidecars-onto-canonical-owner-bundle-loads.md`
  - `ops/tasks/done/RBR-0791-collapse-grouped-replacement-surface-bundle-spec-sidecars-onto-canonical-owner-bundle-loads.md`
