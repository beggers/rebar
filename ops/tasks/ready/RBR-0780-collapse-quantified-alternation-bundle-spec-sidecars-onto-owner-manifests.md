# RBR-0780: Collapse quantified-alternation bundle-spec sidecars onto owner manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached full-manifest `FixtureBundleSpec` layer from `tests/python/test_quantified_alternation_parity_suite.py`; the suite still hand-declares nine `FIXTURE_BUNDLE_SPECS` entries even though all nine published fixture anchors already load cleanly through the canonical owner-manifest path and already derive the same manifest ids, case ids, pattern sets, operation/helper counts, and text-model contracts.
- Make those nine quantified-alternation owner manifests the single source of truth for `FIXTURE_BUNDLES` while keeping the existing bundle aliases, generated parity anchors, direct-bytes follow-on routing, direct-test buckets, backtracking traces, and supplemental no-match coverage unchanged.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining or reading the detached bundle-spec sidecar symbols:
  - `FIXTURE_BUNDLE_SPECS`
  - the file-local `FixtureBundleSpec(...)` declarations
  - the `load_fixture_bundles(...)` call used to build `FIXTURE_BUNDLES`
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- `FIXTURE_BUNDLES` loads the quantified-alternation owner manifests through the canonical full-manifest path instead of the mirrored spec table:
  - define it through `load_published_fixture_bundles(...)`, optionally wrapped in one tiny file-local helper that validates fixture-path and manifest-id order;
  - preserve this fixture path order exactly:
    - `literal_alternation_workflows.py`
    - `exact_repeat_quantified_group_alternation_workflows.py`
    - `quantified_alternation_workflows.py`
    - `quantified_nested_group_alternation_workflows.py`
    - `quantified_alternation_backtracking_heavy_workflows.py`
    - `quantified_alternation_broader_range_workflows.py`
    - `quantified_alternation_conditional_workflows.py`
    - `quantified_alternation_open_ended_workflows.py`
    - `quantified_alternation_nested_branch_workflows.py`
  - preserve the matching manifest ids exactly:
    - `literal-alternation-workflows`
    - `exact-repeat-quantified-group-alternation-workflows`
    - `quantified-alternation-workflows`
    - `quantified-nested-group-alternation-workflows`
    - `quantified-alternation-backtracking-heavy-workflows`
    - `quantified-alternation-broader-range-workflows`
    - `quantified-alternation-conditional-workflows`
    - `quantified-alternation-open-ended-workflows`
    - `quantified-alternation-nested-branch-workflows`
- Each quantified-alternation bundle now derives its contract directly from owner rows instead of mirrored spec metadata:
  - for every bundle in `FIXTURE_BUNDLES`, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_patterns` stays `frozenset(case_pattern(case) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_text_models` stays `frozenset(case.text_model for case in bundle.cases)`.
- Preserve the current suite structure after the cleanup:
  - `QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE`, `QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE`, `QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE`, `QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE`, `QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE`, and `BACKTRACKING_HEAVY_BUNDLE` still resolve through `published_fixture_bundle_by_manifest_id(...)`;
  - `GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS`, `GENERATED_QUANTIFIED_ALTERNATION_COMPILE_CASES`, `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `BACKTRACKING_TRACE_CASES`, and `SUPPLEMENTAL_NO_MATCH_CASES` keep their current ordering and members;
  - keep `test_parity_suite_stays_aligned_with_published_correctness_fixture()`, `test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests()`, `test_quantified_alternation_parity_suite_tracks_published_case_frontier()`, and `test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier()` asserting the same published frontier they cover today; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the mirrored spec table over adding another registry or another shared abstraction layer; and
  - if a helper is useful, keep it file-local to `tests/python/test_quantified_alternation_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles
import tests.python.test_quantified_alternation_parity_suite as mod

fixture_names = (
    "literal_alternation_workflows.py",
    "exact_repeat_quantified_group_alternation_workflows.py",
    "quantified_alternation_workflows.py",
    "quantified_nested_group_alternation_workflows.py",
    "quantified_alternation_backtracking_heavy_workflows.py",
    "quantified_alternation_broader_range_workflows.py",
    "quantified_alternation_conditional_workflows.py",
    "quantified_alternation_open_ended_workflows.py",
    "quantified_alternation_nested_branch_workflows.py",
)
manifest_ids = (
    "literal-alternation-workflows",
    "exact-repeat-quantified-group-alternation-workflows",
    "quantified-alternation-workflows",
    "quantified-nested-group-alternation-workflows",
    "quantified-alternation-backtracking-heavy-workflows",
    "quantified-alternation-broader-range-workflows",
    "quantified-alternation-conditional-workflows",
    "quantified-alternation-open-ended-workflows",
    "quantified-alternation-nested-branch-workflows",
)

bundles = load_published_fixture_bundles(
    tuple(CORRECTNESS_FIXTURES_ROOT / name for name in fixture_names),
    pattern_extractor=case_pattern,
)
assert tuple(bundle.manifest.path.name for bundle in bundles) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in bundles) == manifest_ids
for bundle in bundles:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(case_pattern(case) for case in bundle.cases)
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_text_models == frozenset(
        case.text_model for case in bundle.cases
    )
assert tuple(bundle.manifest.path.name for bundle in mod.FIXTURE_BUNDLES) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in mod.FIXTURE_BUNDLES) == manifest_ids
print("ok")
PY`
  - `bash -lc "! rg -n '^(FIXTURE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_quantified_alternation_parity_suite.py`.
- Do not turn this into a quantified-execution behavior expansion, a fixture-support rewrite, or a multi-suite parity refactor.

## Notes
- `RBR-0780` is the next available task id in the current checkout; the id scan over `ops/tasks/` plus `ops/state/backlog.md` and `ops/state/current_status.md` reported the existing tail through `RBR-0779`, no reserved missing tail ids, and `next_free RBR-0780`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout.
- This cleanup is concrete and viable in the live checkout:
  - `tests/python/test_quantified_alternation_parity_suite.py` currently defines nine full-manifest `FixtureBundleSpec(...)` entries and builds `FIXTURE_BUNDLES` through `load_fixture_bundles(FIXTURE_BUNDLE_SPECS)`;
  - the owner-bundle probe in Acceptance already passes in the current checkout (`ok`);
  - baseline verification is green: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` passed (`778 passed in 1.06s`); and
  - the sidecar-removal probe currently fails exactly on this cleanup boundary by matching the redundant spec table, nine `FixtureBundleSpec(...)` declarations, and the `load_fixture_bundles(...)` call.
- This stays on the same bounded post-JSON simplification track as the adjacent owner-bundle cleanups already landed in:
  - `ops/tasks/done/RBR-0772-collapse-literal-flag-bundle-spec-sidecar-onto-full-manifest-owner.md`
  - `ops/tasks/done/RBR-0776-collapse-parser-matrix-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0778-collapse-open-ended-quantified-group-bundle-spec-sidecars-onto-owner-manifests.md`
