# RBR-0776: Collapse parser-matrix bundle-spec sidecars onto owner manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the remaining selected-case `FixtureBundleSpec` sidecar layer from `tests/python/test_parser_matrix_parity_suite.py`; the suite still hand-declares `SELECTED_CASE_BUNDLE_SPECS` plus `load_fixture_bundles(...)` even though both published fixture anchors can be loaded through the canonical full-manifest owner path and the selected parser frontier can be derived from those owner rows.
- Make `parser_matrix.py` and `conditional_group_exists_assertion_diagnostics.py` the single sources of truth for manifest ids, full published ordering, expected text models, and fixture-bundle metadata in the parser-matrix parity owner.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` stops defining or reading the detached bundle-spec sidecar symbols:
  - `SELECTED_CASE_BUNDLE_SPECS`
  - the file-local `FixtureBundleSpec(...)` entries
  - the `load_fixture_bundles(...)` call
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- The suite loads both published fixture anchors through the canonical owner-manifest path instead of through handwritten bundle specs:
  - use `load_published_fixture_bundles((CORRECTNESS_FIXTURES_ROOT / "parser_matrix.py", CORRECTNESS_FIXTURES_ROOT / "conditional_group_exists_assertion_diagnostics.py"))`, or one equally direct file-local wrapper over that owner-bundle load;
  - preserve manifest path `parser_matrix.py` with manifest id `parser-matrix`; and
  - preserve manifest path `conditional_group_exists_assertion_diagnostics.py` with manifest id `conditional-group-exists-assertion-diagnostics`.
- Derive the selected parser frontier directly from owner rows instead of from duplicated bundle metadata:
  - preserve `EXPECTED_CASE_IDS` exactly as the ordered selected parser slice;
  - preserve `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS == ("str-literal-success", "bytes-literal-success")` exactly as the ordered uncovered remainder of the published parser manifest; and
  - preserve `EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS` exactly as the ordered conditional-assertion diagnostic frontier.
- Keep the current parser-matrix coverage shape unchanged while deleting the sidecar:
  - do not change `TARGET_CASES`, `COMPILE_METADATA_CASES`, `PLACEHOLDER_SEARCH_CASES`, `REPEATED_COMPILE_CACHE_CASES`, `DIAGNOSTIC_CASES`, `NO_STDLIB_DELEGATION_CASES`, `NESTED_SET_WARNING_CASE`, `CHARACTER_CLASS_CASE`, `PLACEHOLDER_SEARCH_SUBJECTS`, or `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES` beyond deriving them from owner rows rather than the deleted bundle specs;
  - keep `test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture()` and `test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture()` asserting the same manifest paths and ordered selected case ids they cover today; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, `python/rebar_harness/`, benchmark files, reports, README text, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the redundant bundle-spec layer over introducing another selector registry, another support helper module, or another detached manifest catalog; and
  - if a helper is useful, keep it file-local to `tests/python/test_parser_matrix_parity_suite.py` and derive it from already-loaded owner bundles.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles
import tests.python.test_parser_matrix_parity_suite as mod

parser_owner_bundle, conditional_owner_bundle = load_published_fixture_bundles(
    (
        CORRECTNESS_FIXTURES_ROOT / "parser_matrix.py",
        CORRECTNESS_FIXTURES_ROOT / "conditional_group_exists_assertion_diagnostics.py",
    )
)
assert parser_owner_bundle.manifest.path == CORRECTNESS_FIXTURES_ROOT / "parser_matrix.py"
assert parser_owner_bundle.manifest.manifest_id == "parser-matrix"
assert tuple(case.case_id for case in parser_owner_bundle.cases) == tuple(
    case.case_id for case in parser_owner_bundle.manifest.cases
)
assert parser_owner_bundle.expected_patterns == frozenset(
    case_pattern(case) for case in parser_owner_bundle.cases
)
assert parser_owner_bundle.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in parser_owner_bundle.cases
)
assert parser_owner_bundle.expected_text_models == frozenset({"str", "bytes"})
assert tuple(case.case_id for case in mod.TARGET_CASES) == mod.EXPECTED_CASE_IDS
assert tuple(
    case.case_id
    for case in parser_owner_bundle.manifest.cases
    if case.case_id not in mod.EXPECTED_CASE_IDS
) == mod.KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS

assert conditional_owner_bundle.manifest.path == (
    CORRECTNESS_FIXTURES_ROOT / "conditional_group_exists_assertion_diagnostics.py"
)
assert conditional_owner_bundle.manifest.manifest_id == (
    "conditional-group-exists-assertion-diagnostics"
)
assert tuple(case.case_id for case in conditional_owner_bundle.cases) == tuple(
    case.case_id for case in conditional_owner_bundle.manifest.cases
)
assert conditional_owner_bundle.expected_patterns == frozenset(
    case_pattern(case) for case in conditional_owner_bundle.cases
)
assert conditional_owner_bundle.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in conditional_owner_bundle.cases
)
assert conditional_owner_bundle.expected_text_models == frozenset({"str"})
assert tuple(case.case_id for case in mod.CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES) == (
    mod.EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS
)
print("ok")
PY`
  - `bash -lc "! rg -n '^(SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_parser_matrix_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_parser_matrix_parity_suite.py`.
- Do not turn this into another parser behavior expansion, a fixture-support rewrite, or a multi-suite parity refactor.

## Notes
- `RBR-0776` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0775`, no reserved missing tail ids, and `next_free RBR-0776`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout; and
  - the latest cycle completed both `RBR-0774` and `RBR-0775` cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and viable in the live checkout:
  - `tests/python/test_parser_matrix_parity_suite.py` currently defines `SELECTED_CASE_BUNDLE_SPECS` with exactly two `FixtureBundleSpec(...)` entries and loads them through `load_fixture_bundles(...)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py` currently passes (`61 passed, 29 skipped in 0.12s`);
  - the owner-bundle probe in Acceptance already passes in the current checkout (`ok`); and
  - `bash -lc "rg -n '^(SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_parser_matrix_parity_suite.py"` currently reports the redundant spec tuple and bundle load, so the negative grep in Acceptance fails exactly on this cleanup boundary.
- This stays on the same bounded post-JSON simplification track as the adjacent owner-bundle cleanups:
  - `ops/tasks/done/RBR-0770-collapse-module-workflow-collection-subset-sidecar-onto-owner-helper-partition.md`,
  - `ops/tasks/done/RBR-0772-collapse-literal-flag-bundle-spec-sidecar-onto-full-manifest-owner.md`, and
  - `ops/tasks/done/RBR-0774-collapse-grouped-capture-bundle-spec-sidecars-onto-full-manifest-owners.md`
  already removed the same style of detached selected-case or full-manifest sidecar layer from neighboring parity owners.
