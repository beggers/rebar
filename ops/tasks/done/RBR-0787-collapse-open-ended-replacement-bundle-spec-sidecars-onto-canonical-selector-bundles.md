# RBR-0787: Collapse open-ended replacement bundle-spec sidecars onto canonical selector bundles

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining three whole-manifest `FixtureBundleSpec(...)` entries from the `open-ended-quantified-group-replacement` surface in `tests/python/test_fixture_backed_replacement_parity_suite.py`; that block still duplicates published-manifest ownership, case ordering, expected pattern sets, operation/helper counts, and mixed-text expectations even though the same three owner manifests already load cleanly through the canonical selector path.
- Make the published open-ended replacement selector the only ownership list for that surface while keeping the current mixed-text aliases, pending-bytes follow-on behavior, compile-pattern coverage, template-expand coverage, and supplemental repeated/no-match cases unchanged.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- In `tests/python/test_fixture_backed_replacement_parity_suite.py`, the `ReplacementSurfaceSpec(id="open-ended-quantified-group-replacement")` block stops hand-declaring the three full-manifest `FixtureBundleSpec(...)` entries for:
  - `nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
  - `nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py`
  - `nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py`
- Build that surface through the canonical full-manifest load path instead of the mirrored spec table:
  - use `load_published_fixture_bundles(OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS, pattern_extractor=case_pattern)`, or one equally direct file-local helper over that call; and
  - keep `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS` as the sole published ownership list for the surface.
- Preserve the current open-ended replacement surface after the cleanup:
  - keep the surface-level bundle order as:
    - `nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows`
  - keep `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.replacement_cases`, `module_cases`, `pattern_cases`, `match_group_access_cases`, and `template_expand_cases` unchanged;
  - keep `MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE` and `BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE` resolving the same manifest ids they resolve today;
  - keep the current mixed-text contracts intact:
    - the broader-range replacement bundle still exposes `expected_text_models == frozenset({"bytes", "str"})`;
    - the broader-range conditional replacement bundle still exposes `expected_text_models == frozenset({"bytes", "str"})`; and
    - the plain open-ended replacement bundle stays `str`-only.
- Derive the open-ended bundle contracts from owner rows instead of mirrored sidecars:
  - for every bundle in that surface, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - `expected_patterns` stays `frozenset(case_pattern(case) for case in bundle.cases)`;
  - `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`; and
  - `expected_text_models` stays aligned with the live text models in each bundle.
- Keep scope structural only:
  - prefer deleting the mirrored sidecars over adding another shared registry or another support layer;
  - if a helper is useful, keep it file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`;
  - do not change the grouped or conditional replacement surface specs in this run beyond any tiny compatibility edit needed to keep this cleanup green; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_fixture_backed_replacement_parity_suite as mod
from tests.python.fixture_parity_support import load_published_fixture_bundles

fixture_names = tuple(
    path.name for path in mod.OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS
)
bundles = load_published_fixture_bundles(
    mod.OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS,
    pattern_extractor=mod.case_pattern,
)
assert tuple(bundle.manifest.path.name for bundle in bundles) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in bundles) == (
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows",
    mod.NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
)
for bundle in bundles:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(
        mod.case_pattern(case) for case in bundle.cases
    )
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
print("ok")
PY`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
import tests.python.test_fixture_backed_replacement_parity_suite as mod

surface = mod.OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE
assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == (
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
    mod.NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
    mod.NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
)
print("ok")
PY`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from pathlib import Path
import re

text = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text()
match = re.search(
    r'^\s*ReplacementSurfaceSpec\(\n\s*id="open-ended-quantified-group-replacement".*?(?=^\s*ReplacementSurfaceSpec\(|^\s*REPLACEMENT_SURFACES = tuple\()',
    text,
    re.M | re.S,
)
assert match is not None
assert "FixtureBundleSpec(" not in match.group(0)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to the open-ended replacement surface inside `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Do not turn this into a whole-file replacement-suite rewrite, a selector-system refactor, or a broader `FixtureBundleSpec` redesign.

## Notes
- `RBR-0787` is free in the current checkout:
  - a repo-local id scan over `ops/tasks/**`, `ops/state/backlog.md`, and `ops/state/current_status.md` reported `next_free RBR-0787`; and
  - no reserved higher `RBR-` ids currently appear in tracked state.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the live checkout before this task is added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and currently viable in the live checkout:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` already passes (`1152 passed in 0.84s`);
  - the canonical owner-bundle probe in Acceptance already passes (`ok`), showing the three owner manifests load cleanly through `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS`;
  - the current surface-order probe in Acceptance already passes (`ok`), so the task can hold the current downstream order steady while deleting the sidecars; and
  - the structural acceptance probe currently fails exactly on this cleanup with `AssertionError` because the `open-ended-quantified-group-replacement` block still contains `FixtureBundleSpec(`.
- This stays on the same post-JSON simplification track as the adjacent owner-bundle cleanups already landed in:
  - `ops/tasks/done/RBR-0778-collapse-open-ended-quantified-group-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0780-collapse-quantified-alternation-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0785-collapse-conditional-replacement-bundle-spec-sidecars-onto-canonical-selector-bundles.md`

## Completion Note
- Removed the three mirrored full-manifest `FixtureBundleSpec(...)` sidecars from the `open-ended-quantified-group-replacement` surface, leaving `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SELECTOR_FIXTURE_PATHS` as the only published ownership list for that surface.
- Added a small file-local bundle-order helper so the surface now loads through `load_published_fixture_bundles(...)`, derives bundle contracts from live owner rows, and still preserves the existing downstream open-ended/broader-range/conditional bundle and case ordering.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` (`1152 passed in 0.88s`) plus the three acceptance probes covering canonical owner-bundle loading (`ok`), downstream surface order (`ok`), and the structural check proving the open-ended surface block no longer contains `FixtureBundleSpec(` (`ok`).
