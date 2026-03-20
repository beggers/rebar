# RBR-0785: Collapse conditional replacement bundle-spec sidecars onto canonical selector bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the ten whole-manifest `FixtureBundleSpec(...)` entries from the `conditional-group-exists-replacement` surface in `tests/python/test_fixture_backed_replacement_parity_suite.py`; that block currently duplicates manifest ownership, case ordering, expected pattern sets, operation/helper counts, and str-only text-model expectations that the shared published-bundle loader can already derive from the owner manifests.
- Make `CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS` the only ownership list for that surface while keeping the current replacement-case partitions, match-snapshot coverage, template-expand coverage, supplemental repeated/no-match cases, and generated param ordering unchanged.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- In `tests/python/test_fixture_backed_replacement_parity_suite.py`, the `ReplacementSurfaceSpec(id="conditional-group-exists-replacement")` block stops hand-declaring the ten full-manifest `FixtureBundleSpec(...)` entries for the conditional replacement workflows.
- Build that surface through the canonical full-manifest load path instead of the mirrored spec table:
  - use `load_published_fixture_bundles(CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS, pattern_extractor=str_case_pattern)`, or one equally direct file-local helper over that call; and
  - preserve the current selector path order and resolved manifest ids exactly.
- Derive the conditional surface bundle contracts from owner rows instead of mirrored sidecars:
  - for every bundle in the conditional surface, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - `expected_patterns` stays `frozenset(str_case_pattern(case) for case in bundle.cases)`;
  - `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`; and
  - `expected_text_models` stays `frozenset({"str"})`.
- Keep the downstream conditional replacement surface unchanged after the cleanup:
  - preserve the current members and ordering of `surface.bundles`, `surface.replacement_cases`, `surface.module_cases`, `surface.pattern_cases`, `surface.match_snapshot_cases`, `surface.template_expand_cases`, `SELECTOR_SURFACE_PARAMS`, `BUNDLE_PARAMS`, and the current supplemental repeated/no-match coverage for the conditional surface;
  - do not change the other two `ReplacementSurfaceSpec(...)` owners in this file;
  - do not remove the later contract tests that still intentionally exercise `FixtureBundleSpec` or `load_fixture_bundles`; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README text, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the mirrored sidecar block over adding another shared registry or a new support layer; and
  - if a helper is useful, keep it file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_fixture_backed_replacement_parity_suite as mod
from tests.python.fixture_parity_support import load_published_fixture_bundles, str_case_pattern

surface = mod._replacement_surface_by_id("conditional-group-exists-replacement")
fixture_names = tuple(path.name for path in mod.CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS)
manifest_ids = (
    "conditional-group-exists-alternation-replacement-workflows",
    "conditional-group-exists-empty-else-replacement-workflows",
    "conditional-group-exists-empty-yes-else-replacement-workflows",
    "conditional-group-exists-fully-empty-replacement-workflows",
    "conditional-group-exists-nested-replacement-workflows",
    "conditional-group-exists-no-else-replacement-workflows",
    "conditional-group-exists-quantified-alternation-replacement-workflows",
    "conditional-group-exists-quantified-replacement-workflows",
    "conditional-group-exists-replacement-template-workflows",
    "conditional-group-exists-replacement-workflows",
)
bundles = load_published_fixture_bundles(
    mod.CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS,
    pattern_extractor=str_case_pattern,
)
assert tuple(bundle.manifest.path.name for bundle in bundles) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in bundles) == manifest_ids
assert tuple(bundle.manifest.path.name for bundle in surface.bundles) == fixture_names
assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == manifest_ids
for bundle in surface.bundles:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(
        str_case_pattern(case) for case in bundle.cases
    )
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_text_models == frozenset({"str"})
print("ok")
PY`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from pathlib import Path
import re

text = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text()
match = re.search(
    r'^\s*ReplacementSurfaceSpec\(\n\s*id="conditional-group-exists-replacement".*?(?=^\s*REPLACEMENT_SURFACES = tuple\(|^\s*ReplacementSurfaceSpec\()',
    text,
    re.M | re.S,
)
assert match is not None
assert "FixtureBundleSpec(" not in match.group(0)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to the conditional replacement surface inside `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Do not turn this into a whole-file replacement-suite rewrite, a fixture-support refactor, or a multi-surface consolidation pass.

## Notes
- `RBR-0785` is free in the current checkout:
  - `ops/tasks/**` currently tops out at `RBR-0784`; and
  - `rg -n "RBR-0(78[5-9]|79[0-9]|8[0-9]{2})" ops/state/current_status.md ops/state/backlog.md` returned no reserved higher ids to skip.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`; and
  - the latest cycle completed `RBR-0784`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and currently viable in the live checkout:
  - the canonical owner-bundle probe in Acceptance already passes in the current checkout (`ok`);
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently contains `10` `FixtureBundleSpec(` occurrences inside the conditional replacement surface block;
  - the structural acceptance probe currently fails with `AssertionError`, which belongs exactly to this cleanup because that block still contains `FixtureBundleSpec(`; and
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1152 passed in 0.84s`).
- This stays on the same post-JSON simplification track as the adjacent owner-bundle cleanups already landed in:
  - `ops/tasks/done/RBR-0778-collapse-open-ended-quantified-group-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0780-collapse-quantified-alternation-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0782-collapse-remaining-owner-manifest-loader-wrappers-onto-canonical-bundle-loads.md`
