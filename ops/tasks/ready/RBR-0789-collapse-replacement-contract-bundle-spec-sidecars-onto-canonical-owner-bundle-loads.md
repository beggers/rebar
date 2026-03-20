# RBR-0789: Collapse replacement contract bundle-spec sidecars onto canonical owner-bundle loads

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining full-manifest `FixtureBundleSpec(...)` sidecars from the replacement parity suite's contract tests in `tests/python/test_fixture_backed_replacement_parity_suite.py`. Those blocks currently restate fixture path, manifest id, expected patterns, operation/helper counts, and text-model expectations even though the same published owner manifests already load cleanly through `load_published_fixture_bundles(...)`.
- Keep the one selected-case grouped collection sidecar explicit for now; this task only deletes the mirrored full-manifest contract sidecars that no longer add ownership information.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` stops using full-manifest `FixtureBundleSpec(...)` / `load_fixture_bundles(...)` plumbing in exactly these four owner-contract blocks:
  - `test_broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on`
  - `test_mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on`
  - `test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier`
  - `test_sorted_compile_patterns_supports_mixed_text_models`
- Rebuild those four checks through canonical owner-bundle loads instead of mirrored sidecars:
  - for the three one-manifest `_load_surface(...)` contract checks, use `selector_fixture_paths=(bundle.manifest.path,)`, `selector_fixture_paths=(BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.manifest.path,)`, `selector_fixture_paths=(MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE.manifest.path,)`, or one equally direct file-local wrapper over the same owner path; and
  - for `test_sorted_compile_patterns_supports_mixed_text_models`, load `open_ended_quantified_group_alternation_workflows.py` through `load_published_fixture_bundles((CORRECTNESS_FIXTURES_ROOT / "open_ended_quantified_group_alternation_workflows.py",), pattern_extractor=case_pattern)` or one equally direct file-local helper over that call.
- Preserve behavior after the cleanup:
  - the three contract tests still validate the same manifest ids they validate today;
  - the three contract tests still validate the same selected versus uncovered bytes routing they validate today;
  - `test_sorted_compile_patterns_supports_mixed_text_models` still asserts the same mixed `str`/`bytes` compile-pattern ordering; and
  - do not change `GROUPED_REPLACEMENT_TEMPLATE_SURFACE`, its selected collection subset, the open-ended replacement surface order, supplemental replacement cases, or any published fixture module contents.
- Keep scope structural only:
  - prefer deleting the mirrored sidecars over adding another shared registry or another support layer;
  - if a helper is useful, keep it file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`; and
  - do not edit `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python .venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import load_published_fixture_bundles
import tests.python.test_fixture_backed_replacement_parity_suite as mod

for path, manifest_id, pattern_extractor in [
    (
        mod.BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.manifest.path,
        mod.NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
        mod.case_pattern,
    ),
    (
        mod.MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE.manifest.path,
        mod.NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
        mod.case_pattern,
    ),
    (
        CORRECTNESS_FIXTURES_ROOT / "open_ended_quantified_group_alternation_workflows.py",
        "open-ended-quantified-group-alternation-workflows",
        mod.case_pattern,
    ),
]:
    (bundle,) = load_published_fixture_bundles((path,), pattern_extractor=pattern_extractor)
    assert bundle.expected_manifest_id == manifest_id
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(
        pattern_extractor(case) for case in bundle.cases
    )
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
print("ok")
PY`
  - `python3 - <<'PY'
from pathlib import Path
import re

text = Path("tests/python/test_fixture_backed_replacement_parity_suite.py").read_text()
patterns = [
    r'^def test_broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on\\(.*?(?=^def |^@|\\Z)',
    r'^def test_mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on\\(.*?(?=^def |^@|\\Z)',
    r'^def test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier\\(.*?(?=^def |^@|\\Z)',
    r'^def test_sorted_compile_patterns_supports_mixed_text_models\\(.*?(?=^def |^@|\\Z)',
]
for pattern in patterns:
    match = re.search(pattern, text, re.M | re.S)
    assert match is not None, pattern
    block = match.group(0)
    assert "FixtureBundleSpec(" not in block
    assert "load_fixture_bundles(" not in block
print("ok")
PY`

## Constraints
- Keep this cleanup limited to the four full-manifest contract sidecars above inside `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Do not broaden into the grouped replacement surface's selected collection subset, a whole-file replacement-suite rewrite, or a `FixtureBundleSpec` redesign.

## Notes
- `RBR-0789` is free in the current checkout:
  - `rg -n "RBR-0789|RBR-0790|RBR-0791|RBR-0792" ops/state/backlog.md ops/state/current_status.md ops/tasks` returned no matches; and
  - a repo-local task scan reported `next_free RBR-0789`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and viable in the current checkout:
  - `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1152 passed in 0.83s`);
  - the owner-bundle probe in Acceptance already passes (`ok`), showing the four contract checks can be rebuilt directly from published owner paths; and
  - the structural acceptance probe currently fails exactly on this cleanup with `AssertionError` because those four blocks still contain `FixtureBundleSpec(` / `load_fixture_bundles(`.
- This stays on the same post-JSON replacement-harness cleanup track as:
  - `ops/tasks/done/RBR-0713-collapse-grouped-replacement-manifest-id-sidecars-onto-surface-spec.md`
  - `ops/tasks/done/RBR-0785-collapse-conditional-replacement-bundle-spec-sidecars-onto-canonical-selector-bundles.md`
  - `ops/tasks/done/RBR-0787-collapse-open-ended-replacement-bundle-spec-sidecars-onto-canonical-selector-bundles.md`
