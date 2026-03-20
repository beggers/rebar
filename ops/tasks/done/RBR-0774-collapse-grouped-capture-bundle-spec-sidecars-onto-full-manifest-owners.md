# RBR-0774: Collapse grouped-capture bundle-spec sidecars onto full-manifest owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached full-manifest `FixtureBundleSpec` layer from `tests/python/test_grouped_capture_parity_suite.py`; all eight `SELECTED_CASE_BUNDLE_SPECS` entries currently mirror whole published manifests exactly, so the suite is maintaining duplicate manifest ids, case-id frontiers, pattern sets, operation/helper counts, and text-model expectations even though the published owner manifests already provide that contract.
- Make the eight grouped-capture fixture owners the only source of truth for `FIXTURE_BUNDLES` while keeping the existing grouped-capture case owners, frontier tests, and direct-test buckets unchanged.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` stops defining or reading the detached bundle-spec sidecar symbols:
  - `SELECTED_CASE_BUNDLE_SPECS`
  - the file-local `FixtureBundleSpec(...)` declarations
  - the `load_fixture_bundles(...)` call used to build `FIXTURE_BUNDLES`
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- `FIXTURE_BUNDLES` loads the grouped-capture owner manifests through the canonical full-manifest path instead of the mirrored spec table:
  - define it through `load_published_fixture_bundles(..., pattern_extractor=str_case_pattern)` or one equally direct file-local wrapper over that helper;
  - preserve this fixture path order exactly:
    - `grouped_match_workflows.py`
    - `named_group_workflows.py`
    - `grouped_segment_workflows.py`
    - `grouped_alternation_workflows.py`
    - `optional_group_workflows.py`
    - `optional_group_alternation_workflows.py`
    - `nested_group_workflows.py`
    - `nested_group_alternation_workflows.py`
  - preserve the matching manifest ids exactly:
    - `grouped-match-workflows`
    - `named-group-workflows`
    - `grouped-segment-workflows`
    - `grouped-alternation-workflows`
    - `optional-group-workflows`
    - `optional-group-alternation-workflows`
    - `nested-group-workflows`
    - `nested-group-alternation-workflows`
- Each grouped-capture bundle now derives its contract directly from owner rows instead of mirrored spec metadata:
  - for every bundle in `FIXTURE_BUNDLES`, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_patterns` stays `frozenset(str_case_pattern(case) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_text_models` stays `frozenset({"str"})`.
- Preserve the current grouped-capture owner lookups and coverage surfaces after the cleanup:
  - `GROUPED_MATCH_FIXTURE_BUNDLE` and `GROUPED_SEGMENT_FIXTURE_BUNDLE` still resolve through `published_fixture_bundle_by_manifest_id(...)`;
  - `PUBLISHED_CASES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `CASES_BY_ID`, and `GROUPED_SEGMENT_LEADING_CAPTURE_CASES` keep their current ordering and members;
  - keep `GROUPED_MATCH_TRACKED_CASE_IDS`, `GROUPED_CAPTURE_TRACKED_CASE_IDS`, `_grouped_match_frontier_contract_case_ids()`, and `_grouped_capture_direct_test_case_id_buckets()` behavior unchanged;
  - do not change grouped-capture behavior tests, supplemental miss cases, bounded-pattern cases, fixture modules under `tests/conformance/fixtures/`, shared fixture-support code, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the mirrored spec table over adding another registry or another shared abstraction layer;
  - keep any helper added for this cleanup file-local to `tests/python/test_grouped_capture_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_grouped_capture_parity_suite as mod

fixture_names = (
    "grouped_match_workflows.py",
    "named_group_workflows.py",
    "grouped_segment_workflows.py",
    "grouped_alternation_workflows.py",
    "optional_group_workflows.py",
    "optional_group_alternation_workflows.py",
    "nested_group_workflows.py",
    "nested_group_alternation_workflows.py",
)
manifest_ids = (
    "grouped-match-workflows",
    "named-group-workflows",
    "grouped-segment-workflows",
    "grouped-alternation-workflows",
    "optional-group-workflows",
    "optional-group-alternation-workflows",
    "nested-group-workflows",
    "nested-group-alternation-workflows",
)
assert tuple(bundle.manifest.path.name for bundle in mod.FIXTURE_BUNDLES) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in mod.FIXTURE_BUNDLES) == manifest_ids
for bundle in mod.FIXTURE_BUNDLES:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(
        mod.str_case_pattern(case) for case in bundle.cases
    )
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_text_models == frozenset({"str"})
assert mod.GROUPED_MATCH_FIXTURE_BUNDLE.manifest.manifest_id == "grouped-match-workflows"
assert mod.GROUPED_SEGMENT_FIXTURE_BUNDLE.manifest.manifest_id == "grouped-segment-workflows"
print("ok")
PY`
  - `bash -lc "! rg -n '^(SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_grouped_capture_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_grouped_capture_parity_suite.py`.
- Do not turn this into a grouped-capture behavior rewrite, a shared fixture-support refactor, or a broader parity-suite consolidation pass.

## Notes
- `RBR-0774` is the next available task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0773`, no reserved missing tail ids, and `next_free RBR-0774`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed `RBR-0772` and `RBR-0773` cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` passed (`427 passed in 0.32s`);
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, load_fixture_manifest
import tests.python.test_grouped_capture_parity_suite as mod

fixture_names = (
    'grouped_match_workflows.py',
    'named_group_workflows.py',
    'grouped_segment_workflows.py',
    'grouped_alternation_workflows.py',
    'optional_group_workflows.py',
    'optional_group_alternation_workflows.py',
    'nested_group_workflows.py',
    'nested_group_alternation_workflows.py',
)
for spec in mod.SELECTED_CASE_BUNDLE_SPECS:
    manifest = load_fixture_manifest(CORRECTNESS_FIXTURES_ROOT / spec.fixture_name)
    assert tuple(spec.selected_case_ids) == tuple(case.case_id for case in manifest.cases)
assert tuple(spec.fixture_name for spec in mod.SELECTED_CASE_BUNDLE_SPECS) == fixture_names
print('ok')
PY` passed (`ok`), confirming every grouped-capture spec is already a full-manifest mirror in manifest order;
  - the canonical owner-load path already supports this suite shape:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import load_published_fixture_bundles, str_case_pattern

fixture_names = (
    'grouped_match_workflows.py',
    'named_group_workflows.py',
    'grouped_segment_workflows.py',
    'grouped_alternation_workflows.py',
    'optional_group_workflows.py',
    'optional_group_alternation_workflows.py',
    'nested_group_workflows.py',
    'nested_group_alternation_workflows.py',
)
bundles = load_published_fixture_bundles(
    tuple(CORRECTNESS_FIXTURES_ROOT / name for name in fixture_names),
    pattern_extractor=str_case_pattern,
)
assert tuple(bundle.manifest.path.name for bundle in bundles) == fixture_names
for bundle in bundles:
    assert tuple(case.case_id for case in bundle.cases) == tuple(case.case_id for case in bundle.manifest.cases)
    assert bundle.expected_patterns == frozenset(str_case_pattern(case) for case in bundle.cases)
    assert bundle.expected_text_models == frozenset({'str'})
print('ok')
PY` passed (`ok`); and
  - `bash -lc "rg -n '^(SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_grouped_capture_parity_suite.py"` currently reports the eight redundant `FixtureBundleSpec` lines plus the single `load_fixture_bundles(...)` call, so the negative grep in Acceptance fails exactly on this cleanup boundary.

## Completion Note
- Replaced the detached `SELECTED_CASE_BUNDLE_SPECS` table with a direct `load_published_fixture_bundles(...)` call over the eight grouped-capture owner manifests in the required order, using `pattern_extractor=str_case_pattern`.
- Left the grouped-capture case buckets, ordered frontier helpers, and `published_fixture_bundle_by_manifest_id(...)` owner lookups unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`, the manifest-order/bundle-contract Python probe from Acceptance, and the negative grep proving the sidecar symbols are gone.
