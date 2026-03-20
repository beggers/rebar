# RBR-0778: Collapse open-ended quantified-group bundle-spec sidecars onto owner manifests

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached full-manifest `FixtureBundleSpec` layer from `tests/python/test_open_ended_quantified_group_parity_suite.py`; all seven `FIXTURE_BUNDLE_SPECS` entries currently mirror whole published manifests exactly, so the suite is maintaining duplicate manifest ids, pattern sets, operation/helper counts, and mixed text-model expectations even though the published owner manifests already provide that contract.
- Make the seven open-ended quantified-group fixture owners the only source of truth for `FIXTURE_BUNDLES` while keeping the existing bundle lookups, direct-bytes follow-on routing, trace bundles, direct-test buckets, and bounded-pattern coverage unchanged.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining or reading the detached bundle-spec sidecar symbols:
  - `FIXTURE_BUNDLE_SPECS`
  - the file-local `FixtureBundleSpec(...)` declarations
  - the `load_fixture_bundles(...)` call used to build `FIXTURE_BUNDLES`
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- `FIXTURE_BUNDLES` loads the open-ended owner manifests through the canonical full-manifest path instead of the mirrored spec table:
  - define it through `load_published_fixture_bundles(...)`, optionally wrapped in one tiny file-local helper that validates manifest ids;
  - preserve this fixture path order exactly:
    - `open_ended_quantified_group_alternation_workflows.py`
    - `open_ended_quantified_group_alternation_conditional_workflows.py`
    - `open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
    - `broader_range_open_ended_quantified_group_alternation_workflows.py`
    - `broader_range_open_ended_quantified_group_alternation_conditional_workflows.py`
    - `broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
    - `nested_open_ended_quantified_group_alternation_workflows.py`
  - preserve the matching manifest ids exactly:
    - `open-ended-quantified-group-alternation-workflows`
    - `open-ended-quantified-group-alternation-conditional-workflows`
    - `open-ended-quantified-group-alternation-backtracking-heavy-workflows`
    - `broader-range-open-ended-quantified-group-alternation-workflows`
    - `broader-range-open-ended-quantified-group-alternation-conditional-workflows`
    - `broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows`
    - `nested-open-ended-quantified-group-alternation-workflows`
- Each open-ended quantified-group bundle now derives its contract directly from owner rows instead of mirrored spec metadata:
  - for every bundle in `FIXTURE_BUNDLES`, `tuple(case.case_id for case in bundle.cases)` stays equal to `tuple(case.case_id for case in bundle.manifest.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_patterns` stays `frozenset(case_pattern(case) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in bundle.cases)`;
  - for every bundle in `FIXTURE_BUNDLES`, `expected_text_models` stays `frozenset({"str", "bytes"})`.
- Preserve the current suite structure after the cleanup:
  - `OPEN_ENDED_ALTERNATION_BUNDLE`, `OPEN_ENDED_CONDITIONAL_BUNDLE`, `OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`, and `NESTED_OPEN_ENDED_ALTERNATION_BUNDLE` still resolve through `published_fixture_bundle_by_manifest_id(...)`;
  - `OPEN_ENDED_TRACE_BUNDLES`, `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `OPEN_ENDED_BYTES_CASE_SURFACES`, `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `_open_ended_quantified_group_direct_test_case_id_buckets()`, and the bounded-pattern case buckets keep their current ordering and members;
  - keep `test_parity_suite_stays_aligned_with_published_correctness_fixture()` and `test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier()` asserting the same published frontier they cover today; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the mirrored spec table over adding another registry or another shared abstraction layer; and
  - if a helper is useful, keep it file-local to `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles
import tests.python.test_open_ended_quantified_group_parity_suite as mod

fixture_names = (
    "open_ended_quantified_group_alternation_workflows.py",
    "open_ended_quantified_group_alternation_conditional_workflows.py",
    "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
    "nested_open_ended_quantified_group_alternation_workflows.py",
)
manifest_ids = (
    "open-ended-quantified-group-alternation-workflows",
    "open-ended-quantified-group-alternation-conditional-workflows",
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
    "broader-range-open-ended-quantified-group-alternation-workflows",
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
    "nested-open-ended-quantified-group-alternation-workflows",
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
    assert bundle.expected_text_models == frozenset({"str", "bytes"})
assert tuple(bundle.manifest.path.name for bundle in mod.FIXTURE_BUNDLES) == fixture_names
assert tuple(bundle.manifest.manifest_id for bundle in mod.FIXTURE_BUNDLES) == manifest_ids
print("ok")
PY`
  - `bash -lc "! rg -n '^(FIXTURE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Do not turn this into an open-ended execution rewrite, a shared fixture-support refactor, or a multi-suite parity consolidation pass.

## Notes
- `RBR-0778` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0777`, no reserved missing tail ids, and `next_free RBR-0778`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed `RBR-0776` and `RBR-0777` cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently defines seven full-manifest `FixtureBundleSpec(...)` entries and builds `FIXTURE_BUNDLES` through `load_fixture_bundles(FIXTURE_BUNDLE_SPECS)`;
  - the canonical owner-load path already supports this suite shape:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles

fixture_names = (
    'open_ended_quantified_group_alternation_workflows.py',
    'open_ended_quantified_group_alternation_conditional_workflows.py',
    'open_ended_quantified_group_alternation_backtracking_heavy_workflows.py',
    'broader_range_open_ended_quantified_group_alternation_workflows.py',
    'broader_range_open_ended_quantified_group_alternation_conditional_workflows.py',
    'broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py',
    'nested_open_ended_quantified_group_alternation_workflows.py',
)
bundles = load_published_fixture_bundles(
    tuple(CORRECTNESS_FIXTURES_ROOT / name for name in fixture_names),
    pattern_extractor=case_pattern,
)
for bundle in bundles:
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_patterns == frozenset(case_pattern(case) for case in bundle.cases)
    assert bundle.expected_operation_helper_counts == Counter(
        (case.operation, case.helper) for case in bundle.cases
    )
    assert bundle.expected_text_models == frozenset({'str', 'bytes'})
print('ok')
PY` passed (`ok`);
  - baseline verification is green:
    - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passed (`3902 passed in 2.63s`);
  - and the sidecar-removal probe currently fails exactly on this cleanup boundary:
    - `bash -lc "! rg -n '^(FIXTURE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_open_ended_quantified_group_parity_suite.py"` currently reports the redundant spec table and bundle load.
- This stays on the same bounded post-JSON simplification track as the adjacent owner-bundle cleanups already landed in:
  - `ops/tasks/done/RBR-0772-collapse-literal-flag-bundle-spec-sidecar-onto-full-manifest-owner.md`
  - `ops/tasks/done/RBR-0774-collapse-grouped-capture-bundle-spec-sidecars-onto-full-manifest-owners.md`
  - `ops/tasks/done/RBR-0776-collapse-parser-matrix-bundle-spec-sidecars-onto-owner-manifests.md`

## Completion Note
- Replaced the open-ended quantified-group parity suite's detached `FixtureBundleSpec` table with a file-local owner-manifest loader built on `load_published_fixture_bundles(...)`, preserving the exact seven fixture paths, matching manifest ids, and existing bundle aliases.
- Kept `FIXTURE_BUNDLES` as the single published-bundle source for the suite's selected-case ids, trace bundles, bytes follow-on routing, direct-test buckets, and bounded-pattern coverage while deriving expected patterns, operation/helper counts, and text-model contracts directly from owner rows.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`, the acceptance owner-bundle probe (`ok`), and the negative grep proving `FIXTURE_BUNDLE_SPECS`, `FixtureBundleSpec(...)`, and `load_fixture_bundles(...)` are gone from the suite.
