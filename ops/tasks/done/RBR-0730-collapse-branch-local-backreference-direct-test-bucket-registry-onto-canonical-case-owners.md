# RBR-0730: Collapse branch-local-backreference direct-test bucket registry onto canonical case owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_branch_local_backreference_parity_suite.py` so the shared branch-local-backreference parity owner derives direct-test bucket coverage from its canonical shared case owners plus the existing direct bytes follow-on specs instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining or reading `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS`.
- The branch-local-backreference direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor` no longer indexes the deleted registry for the per-bundle bytes-follow-on bucket check.
- Preserve the current effective bucket ordering and membership exactly:
  - the bucket keys stay `shared-compile`, `shared-module`, `shared-pattern`, `quantified-alternation-branch-local-backreference-bytes-follow-on`, `quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, and `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on` in that order;
  - `shared-compile` still equals `frozenset(case.case_id for case in COMPILE_CASES)`;
  - `shared-module` still equals `frozenset(case.case_id for case in MODULE_CASES)`;
  - `shared-pattern` still equals `frozenset(case.case_id for case in PATTERN_CASES)`; and
  - each bytes-follow-on bucket still equals `frozenset(case.case_id for case in spec.bundle.cases if case.text_model == "bytes")` keyed by `_direct_bytes_follow_on_bucket_label(spec.bundle)` for the same `DIRECT_BYTES_FOLLOW_ON_SPECS` iteration order that exists today.
- If a tiny file-local helper is useful, keep it derived from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `DIRECT_BYTES_FOLLOW_ON_SPECS`, and `_direct_bytes_follow_on_bucket_label()` instead of introducing another mirrored tuple/list/map block.
- Keep canonical ownership otherwise unchanged:
  - do not change `FIXTURE_BUNDLES`, `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_CASES`, `SUPPORTED_DIRECT_BYTES_PATTERNS`, `PUBLISHED_CASES`, `CASES_BY_ID`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `WORKFLOW_CASES`, `BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS`, `MATCH_CONVENIENCE_MANIFEST_IDS`, `MATCH_CONVENIENCE_CASE_IDS`, or the direct bytes follow-on case definitions carried in this file;
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret branch-local-backreference frontier ownership, move case ids between buckets, or add another abstraction layer beyond a tiny file-local helper if one is needed.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_branch_local_backreference_parity_suite as mod

derived = {
    "shared-compile": frozenset(case.case_id for case in mod.COMPILE_CASES),
    "shared-module": frozenset(case.case_id for case in mod.MODULE_CASES),
    "shared-pattern": frozenset(case.case_id for case in mod.PATTERN_CASES),
    **{
        mod._direct_bytes_follow_on_bucket_label(spec.bundle): frozenset(
            case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
        )
        for spec in mod.DIRECT_BYTES_FOLLOW_ON_SPECS
    },
}
assert tuple(derived) == (
    "shared-compile",
    "shared-module",
    "shared-pattern",
    "quantified-alternation-branch-local-backreference-bytes-follow-on",
    "quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS,
    coverage_label="branch-local-backreference direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one mirrored direct-test owner layer inside the shared branch-local-backreference parity suite, not to reinterpret branch-local-backreference semantics or widen the test surface.
- Prefer deriving direct-test bucket coverage directly from the existing shared case owners and direct bytes follow-on specs over introducing another detached helper registry.

## Notes
- `RBR-0730` is the next available architecture-task id in the current checkout:
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
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-10:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 80):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0729`, no reserved missing tail ids, and `next_free RBR-0730`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`9b7e736b477f2225274c94a65933735ddcb34d1c`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers completing and the harness committing and pushing cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached branch-local-backreference bucket registry is concrete and bounded in the current checkout:
  - `rg -n 'BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS|test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier|test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor' tests/python/test_branch_local_backreference_parity_suite.py` shows the registry is declared once and only consumed by the selected-frontier coverage test plus the direct bytes follow-on anchor assertion in this file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read twice in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as the recent architecture work:
  - `ops/tasks/done/RBR-0721-collapse-quantified-alternation-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0723-collapse-wider-ranged-repeat-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0727-collapse-open-ended-direct-test-bucket-sidecar-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0728-collapse-grouped-capture-direct-test-bucket-registry-onto-canonical-case-owners.md`, and `ops/tasks/done/RBR-0729-collapse-parser-matrix-direct-test-bucket-registry-onto-canonical-case-owners.md` already removed the same style of detached direct-test owner layer from adjacent parity suites; and
  - `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` is the same style of mirrored owner data, but here the canonical sources are the shared branch-local compile/module/pattern case owners plus the direct bytes follow-on specs that already live in this file.
- 2026-03-20 completion:
  - Removed `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` from `tests/python/test_branch_local_backreference_parity_suite.py`.
  - Added a tiny file-local helper that derives the direct-test bucket map from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `DIRECT_BYTES_FOLLOW_ON_SPECS`, and `_direct_bytes_follow_on_bucket_label()`, preserving the existing bucket ordering and membership.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` (`561 passed in 0.84s`), the derived-bucket probe from the task (`ok`), and the `rg` absence check for `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` (no matches).
