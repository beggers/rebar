# RBR-0799: Collapse generated quantified conditional spec sidecars onto live bundle metadata

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining generated-spec sidecars from `tests/python/test_conditional_group_exists_parity_suite.py` that duplicate data the suite already owns elsewhere.
- Keep the generated quantified conditional parity checks deriving manifest-path anchoring from the live `FixtureBundle` objects and candidate-count expectations from the generated candidate-text table instead of storing duplicate `fixture_name` and `expected_candidate_count` fields on each spec row.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` no longer defines or references:
  - `GeneratedQuantifiedConditionalParitySpec.fixture_name`; or
  - `GeneratedQuantifiedConditionalParitySpec.expected_candidate_count`.
- Every `GeneratedQuantifiedConditionalParitySpec(...)` entry stops passing `fixture_name=...` and `expected_candidate_count=...`.
- `test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests()` still proves the same two generated quantified conditional manifests stay anchored to the published correctness fixtures, but it derives those facts from the live bundle metadata and generated candidate-text table instead of the deleted sidecars:
  - preserve the existing checks over `expected_compile_case_ids`, `expected_patterns`, and the current `{"str"}` text-model contract;
  - keep the manifest-path anchoring tied to `spec.bundle.manifest.path` / the already loaded published bundles rather than another copied file-name field; and
  - keep the candidate-count assertion tied to `GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID` rather than another stored integer.
- Preserve the current conditional parity surface and verification behavior:
  - keep `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS`, `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPEC_BY_MANIFEST_ID`, `GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID`, the bounded-pattern cases, the optional-group conditional branch cases, and the supplemental fullmatch/miss coverage intact;
  - do not change fixture modules under `tests/conformance/fixtures/`, harness code under `python/rebar_harness/`, benchmarks, reports, README copy, or tracked project-state prose; and
  - do not broaden into feature work or parity-behavior changes.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n 'fixture_name: str|expected_candidate_count: int|fixture_name=|expected_candidate_count=|spec\\.fixture_name|spec\\.expected_candidate_count' tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_conditional_group_exists_parity_suite.py`.
- Prefer deleting duplicated generated-spec metadata over adding another helper registry or another shared abstraction.

## Notes
- `RBR-0799` is free in the current checkout:
  - `rg -n "RBR-0799|RBR-0800|RBR-0801" ops/state/backlog.md ops/state/current_status.md` returned no reserved `RBR-0799`-series matches in this run; and
  - the repo-local next-free-id probe reported `RBR-0799`.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.48s`);
  - `rg -n "fixture_name: str|expected_candidate_count: int|fixture_name=|expected_candidate_count=|spec\\.fixture_name|spec\\.expected_candidate_count" tests/python/test_conditional_group_exists_parity_suite.py` currently reports only this file; and
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
import tests.python.test_conditional_group_exists_parity_suite as mod
expected_counts = {
    "conditional-group-exists-quantified-workflows": 32,
    "conditional-group-exists-quantified-alternation-workflows": 128,
}
for spec in mod.GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS:
    assert spec.bundle.manifest.path.name.endswith(".py")
    assert len(
        mod.GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
            spec.bundle.expected_manifest_id
        ]
    ) == expected_counts[spec.bundle.expected_manifest_id]
print("ok")
PY` currently passes (`ok`), showing both sidecars are still live and are duplicating facts already available from the bundle metadata and generated candidate-text table.
- This follows the same post-JSON generated-spec sidecar-removal track as:
  - `ops/tasks/done/RBR-0797-collapse-generated-quantified-alternation-spec-sidecars-onto-live-bundle-metadata.md`
