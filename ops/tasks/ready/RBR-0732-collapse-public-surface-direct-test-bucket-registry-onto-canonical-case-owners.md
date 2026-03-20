# RBR-0732: Collapse public-surface direct-test bucket registry onto canonical case owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_module_workflow_parity_suite.py` so the public-surface parity owner derives direct-test bucket coverage from its canonical case owners instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS`.
- The public-surface direct-test coverage derives from the existing canonical case owners instead of from the deleted registry:
  - `test_public_surface_direct_test_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map.
- Preserve the current effective bucket ordering and membership exactly:
  - the bucket keys stay `public-helper-presence`, `public-module-call`, `exported-symbol-metadata`, `exported-symbol-value`, `exported-constructor-guard`, `pattern-object-metadata`, and `pattern-object-call` in that order;
  - `public-helper-presence` still equals `frozenset(case.case_id for case in PUBLIC_HELPER_CASES)`;
  - `public-module-call` still equals `frozenset(case.case_id for case in PUBLIC_MODULE_CALL_CASES)`;
  - `exported-symbol-metadata` still equals `frozenset(case.case_id for case in EXPORTED_METADATA_CASES)`;
  - `exported-symbol-value` still equals `frozenset(case.case_id for case in EXPORTED_VALUE_CASES)`;
  - `exported-constructor-guard` still equals `frozenset(case.case_id for case in EXPORTED_CONSTRUCTOR_GUARD_CASES)`;
  - `pattern-object-metadata` still equals `frozenset(case.case_id for case in PATTERN_METADATA_CASES)`; and
  - `pattern-object-call` still equals `frozenset(case.case_id for case in PATTERN_CALL_CASES)`.
- Because the detached map is only consumed once, prefer building the mapping inline at the coverage assertion or via one tiny file-local helper derived directly from `PUBLIC_HELPER_CASES`, `PUBLIC_MODULE_CALL_CASES`, `EXPORTED_METADATA_CASES`, `EXPORTED_VALUE_CASES`, `EXPORTED_CONSTRUCTOR_GUARD_CASES`, `PATTERN_METADATA_CASES`, and `PATTERN_CALL_CASES` instead of introducing another mirrored registry layer.
- Keep canonical ownership otherwise unchanged:
  - do not change `PUBLIC_SURFACE_BUNDLES`, `PUBLIC_API_BUNDLE`, `EXPORTED_SYMBOL_BUNDLE`, `PATTERN_OBJECT_BUNDLE`, `PUBLIC_HELPER_CASES`, `PUBLIC_MODULE_CALL_CASES`, `EXPORTED_METADATA_CASES`, `EXPORTED_VALUE_CASES`, `EXPORTED_CONSTRUCTOR_GUARD_CASES`, `PATTERN_METADATA_CASES`, `PATTERN_CALL_CASES`, `PUBLIC_SURFACE_SELECTED_CASE_IDS`, `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS`, or `LITERAL_COLLECTION_DIRECT_TEST_CASE_ID_BUCKETS`;
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret public-surface ownership, move case ids between buckets, or change any public-surface fixture rows or parity expectations.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_module_workflow_parity_suite as mod

derived = {
    "public-helper-presence": frozenset(case.case_id for case in mod.PUBLIC_HELPER_CASES),
    "public-module-call": frozenset(case.case_id for case in mod.PUBLIC_MODULE_CALL_CASES),
    "exported-symbol-metadata": frozenset(case.case_id for case in mod.EXPORTED_METADATA_CASES),
    "exported-symbol-value": frozenset(case.case_id for case in mod.EXPORTED_VALUE_CASES),
    "exported-constructor-guard": frozenset(
        case.case_id for case in mod.EXPORTED_CONSTRUCTOR_GUARD_CASES
    ),
    "pattern-object-metadata": frozenset(case.case_id for case in mod.PATTERN_METADATA_CASES),
    "pattern-object-call": frozenset(case.case_id for case in mod.PATTERN_CALL_CASES),
}
assert tuple(derived) == (
    "public-helper-presence",
    "public-module-call",
    "exported-symbol-metadata",
    "exported-symbol-value",
    "exported-constructor-guard",
    "pattern-object-metadata",
    "pattern-object-call",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.PUBLIC_SURFACE_SELECTED_CASE_IDS,
    coverage_label="public surface direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one mirrored direct-test owner layer inside the module-workflow parity suite, not to reinterpret module/public-surface behavior or widen the direct-test frontier.
- Prefer deriving direct-test bucket coverage directly from the existing public-surface case owners over introducing another detached helper tuple/list/map.

## Notes
- `RBR-0732` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-12:])
print('reserved_tail', reserved_sorted[-12:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 100):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0731`, no reserved missing tail ids, and `next_free RBR-0732`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`58fcb9ae087bea7585671f62a2a23aa4370d6b74`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers completing and the harness committing and pushing cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached public-surface bucket registry is concrete and bounded in the current checkout:
  - `rg -n 'PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS|test_public_surface_direct_test_buckets_cover_selected_frontier' tests/python/test_module_workflow_parity_suite.py` shows the registry is declared once and only consumed by the selected-frontier coverage test in this file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`581 passed, 1 skipped in 0.44s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as the recent architecture work:
  - `ops/tasks/done/RBR-0727-collapse-open-ended-direct-test-bucket-sidecar-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0728-collapse-grouped-capture-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0729-collapse-parser-matrix-direct-test-bucket-registry-onto-canonical-case-owners.md`, and `ops/tasks/done/RBR-0730-collapse-branch-local-backreference-direct-test-bucket-registry-onto-canonical-case-owners.md` already removed the same style of detached direct-test owner layer from adjacent parity suites; and
  - `PUBLIC_SURFACE_DIRECT_TEST_CASE_ID_BUCKETS` is the same style of mirrored owner data, but here the canonical sources are the existing public-surface case-owner tuples that already live in this file.
